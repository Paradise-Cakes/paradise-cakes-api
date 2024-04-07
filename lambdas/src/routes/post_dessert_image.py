import os
import arrow
import boto3
import uuid
from fastapi import APIRouter, Request, File, UploadFile, Form, HTTPException
from aws_lambda_powertools import Logger
from src.lib.response import fastapi_gateway_response
from src.models import DessertImage
from src.models.base import Base
from src.lib.dynamodb import DynamoConnection


logger = Logger()
router = APIRouter()
s3_client = boto3.client("s3")


dessert_images_table = DynamoConnection(
    os.environ.get("DYNAMODB_REGION", "us-east-1"),
    os.environ.get("DYNAMODB_ENDPOINT_URL", None),
    os.environ.get("DYNAMODB_DESSERT_IMAGES_TABLE_NAME", "dessert_images"),
).table


class PostDessertImageResponse(DessertImage):
    pass


@logger.inject_lambda_context(log_event=True)
@router.post(
    "/desserts/{dessert_id}/images",
    status_code=201,
    response_model=PostDessertImageResponse,
)
def create_image(
    request: Request,
    dessert_id: str,
    file: UploadFile = File(...),
    position: int = Form(...),
):
    logger.info(f"Creating new image for dessert: {dessert_id}")

    image_id = uuid.uuid4()
    created_at = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ss")
    last_updated_at = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ss")

    file_extension = file.filename.split(".")[-1]
    object_name = f"{uuid.uuid4()}.{file_extension}"

    try:
        s3_client.upload_fileobj(
            file.file, os.environ.get("DESSERT_IMAGES_BUCKET_NAME"), object_name
        )
        file_url = f"https://{os.environ.get('DESSERT_IMAGES_BUCKET_NAME')}.s3.amazonaws.com/{dessert_id}/{object_name}"

        new_image = DessertImage(
            position=position,
            file_url=file_url,
            image_id=image_id,
            dessert_id=dessert_id,
            created_at=created_at,
            last_updated_at=last_updated_at,
        )

        dessert_images_table.put_item(Item={**new_image.clean()})
        response = PostDessertImageResponse(**new_image.model_dump())
        logger.info(f"Created new image for dessert: {new_image}")
        return fastapi_gateway_response(201, {}, response.clean())

    except Exception as e:
        logger.exception(f"Error uploading file to S3: {e}")
        raise HTTPException(status_code=500, detail="Error uploading file to S3")
