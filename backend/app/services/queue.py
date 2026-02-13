from __future__ import annotations

from datetime import datetime
from threading import Lock, Thread

from sqlmodel import Session, select

from app.core.db import engine
from app.models import BrandVoice, ExportAsset, JobStatus, Product, RenderJob
from app.services.copygen import generate_pack
from app.services.quality import low_res_images, pick_best_images, repeated_words, safe_area_check, trim_overlay
from app.services.video import render_video

_queue_lock = Lock()
_worker_started = False


def ensure_worker() -> None:
    global _worker_started
    with _queue_lock:
        if _worker_started:
            return
        Thread(target=_worker_loop, daemon=True).start()
        _worker_started = True


def _worker_loop() -> None:
    while True:
        with Session(engine) as session:
            job = session.exec(select(RenderJob).where(RenderJob.status == JobStatus.queued).order_by(RenderJob.created_at)).first()
            if not job:
                session.commit()
            else:
                _run_job(session, job)
        import time

        time.sleep(1)


def _run_job(session: Session, job: RenderJob) -> None:
    job.status = JobStatus.running
    job.progress = 0.1
    job.updated_at = datetime.utcnow()
    session.add(job)
    session.commit()
    session.refresh(job)
    try:
        product = session.get(Product, job.product_id)
        voice = session.get(BrandVoice, 1) or BrandVoice(id=1)
        if not product:
            raise ValueError("Product not found")
        pack = generate_pack(product, voice, variant_index=job.variant_index)
        lines = [pack["hooks"][0], *pack["benefits"], pack["ctas"][0]]
        warnings = safe_area_check(lines)
        dupes = repeated_words(lines)
        lines = [trim_overlay(l) for l in lines]

        images = pick_best_images(product.local_images)
        if not images:
            raise ValueError("No local images for render")
        bad_images = low_res_images(images)
        if bad_images:
            warnings.append(f"Low resolution images detected: {len(bad_images)}")

        job.progress = 0.6
        output_name = f"product-{product.id}-v{job.variant_index}-{job.id}"
        output, srt = render_video(images, lines, output_name)

        export = ExportAsset(
            product_id=product.id,
            job_id=job.id,
            caption=pack["caption"],
            hashtags=pack["hashtags"],
            hooks=pack["hooks"],
            ctas=pack["ctas"],
            filename=output_name + ".mp4",
            location=output,
            srt_path=srt,
        )
        session.add(export)
        job.status = JobStatus.completed
        job.progress = 1.0
        job.output_path = output
        if warnings or dupes:
            job.error = "; ".join(warnings + [f"Repeated words: {','.join(dupes)}"])
    except Exception as exc:
        job.status = JobStatus.failed
        job.error = str(exc)
    finally:
        job.updated_at = datetime.utcnow()
        session.add(job)
        session.commit()
