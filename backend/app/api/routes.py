from __future__ import annotations

import csv
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.db import get_session
from app.models import BrandVoice, ExportAsset, Product, RenderJob, VideoTemplate
from app.services.queue import ensure_worker
from app.services.templates import TEMPLATES

router = APIRouter()
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/health")
def health() -> dict:
    return {"ok": True}


@router.post("/import/csv")
async def import_csv(file: UploadFile = File(...), session: Session = Depends(get_session)):
    payload = await file.read()
    decoded = payload.decode("utf-8", errors="ignore").splitlines()
    reader = csv.DictReader(decoded)
    created = 0
    for row in reader:
        external_id = row.get("product_id") or row.get("handle")
        if not external_id:
            continue
        product = Product(
            external_id=external_id,
            title=row.get("title", "Untitled"),
            price=row.get("price", "0"),
            description=row.get("description", ""),
            image_urls=[u.strip() for u in (row.get("image_urls", "").split("|") if row.get("image_urls") else []) if u.strip()],
        )
        session.add(product)
        created += 1
    session.commit()
    return {"created": created}


@router.post("/products/{product_id}/images")
async def upload_images(product_id: int, files: list[UploadFile] = File(...), session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    product_dir = UPLOAD_DIR / str(product_id)
    product_dir.mkdir(parents=True, exist_ok=True)
    local_images = product.local_images or []
    for file in files:
        path = product_dir / file.filename
        with path.open("wb") as fh:
            shutil.copyfileobj(file.file, fh)
        local_images.append(str(path))

    product.local_images = local_images
    session.add(product)
    session.commit()
    return {"images": local_images}


@router.get("/products")
def list_products(session: Session = Depends(get_session)):
    return session.exec(select(Product).order_by(Product.created_at.desc())).all()


@router.get("/products/{product_id}")
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Not found")
    return product


@router.put("/products/{product_id}")
def update_product_copy(product_id: int, description: str = Form(...), session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Not found")
    product.description = description
    session.add(product)
    session.commit()
    return product


@router.get("/templates")
def list_templates(session: Session = Depends(get_session)):
    existing = {t.key for t in session.exec(select(VideoTemplate)).all()}
    for template in TEMPLATES:
        if template["key"] not in existing:
            session.add(VideoTemplate(**template))
    session.commit()
    return session.exec(select(VideoTemplate)).all()


class QueueRequest(BaseModel):
    product_ids: list[int]
    template_key: str
    variants: int = 1


@router.post("/queue/generate")
def enqueue_jobs(payload: QueueRequest, session: Session = Depends(get_session)):
    ensure_worker()
    jobs = []
    for product_id in payload.product_ids:
        for variant in range(1, payload.variants + 1):
            job = RenderJob(product_id=product_id, template_key=payload.template_key, variant_index=variant)
            session.add(job)
            jobs.append(job)
    session.commit()
    return {"queued": len(jobs)}


@router.get("/queue/jobs")
def queue_jobs(session: Session = Depends(get_session)):
    return session.exec(select(RenderJob).order_by(RenderJob.created_at.desc())).all()


@router.post("/queue/jobs/{job_id}/retry")
def retry_job(job_id: int, session: Session = Depends(get_session)):
    job = session.get(RenderJob, job_id)
    if not job:
        raise HTTPException(404, "Not found")
    job.status = "queued"
    job.error = None
    job.progress = 0
    session.add(job)
    session.commit()
    ensure_worker()
    return job


@router.get("/exports")
def exports(session: Session = Depends(get_session)):
    return session.exec(select(ExportAsset).order_by(ExportAsset.created_at.desc())).all()


@router.get("/brand-voice")
def get_brand_voice(session: Session = Depends(get_session)):
    voice = session.get(BrandVoice, 1)
    if not voice:
        voice = BrandVoice(id=1)
        session.add(voice)
        session.commit()
        session.refresh(voice)
    return voice


@router.put("/brand-voice")
def set_brand_voice(payload: BrandVoice, session: Session = Depends(get_session)):
    payload.id = 1
    session.merge(payload)
    session.commit()
    return payload


@router.post("/audio/upload")
async def upload_audio(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".mp3", ".wav", ".m4a")):
        raise HTTPException(400, "Only user-uploaded audio files are allowed")
    audio_dir = Path("data/audio")
    audio_dir.mkdir(parents=True, exist_ok=True)
    path = audio_dir / file.filename
    with path.open("wb") as fh:
        shutil.copyfileobj(file.file, fh)
    return {"path": str(path)}
