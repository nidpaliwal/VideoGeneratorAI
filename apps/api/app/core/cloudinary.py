import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url
from typing import Optional, Dict, Any, List
import structlog

from app.core.config import settings

logger = structlog.get_logger()

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


class CloudinaryService:
    @staticmethod
    def upload_video(
        file_path: str,
        public_id: Optional[str] = None,
        folder: str = "videogen/videos",
        transformations: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        upload_params = {
            "resource_type": "video",
            "folder": folder,
            "use_filename": True,
            "unique_filename": True,
            "overwrite": False,
        }
        if public_id:
            upload_params["public_id"] = public_id
        if transformations:
            upload_params["eager"] = transformations
            upload_params["eager_async"] = True
        upload_params.update(kwargs)

        logger.info("Uploading video to Cloudinary", public_id=public_id, folder=folder)
        result = cloudinary.uploader.upload(file_path, **upload_params)
        logger.info("Video uploaded to Cloudinary", public_id=result.get("public_id"), url=result.get("secure_url"))
        return result

    @staticmethod
    def upload_image(
        file_path: str,
        public_id: Optional[str] = None,
        folder: str = "videogen/images",
        **kwargs,
    ) -> Dict[str, Any]:
        upload_params = {
            "resource_type": "image",
            "folder": folder,
            "use_filename": True,
            "unique_filename": True,
            "overwrite": False,
        }
        if public_id:
            upload_params["public_id"] = public_id
        upload_params.update(kwargs)

        logger.info("Uploading image to Cloudinary", public_id=public_id, folder=folder)
        result = cloudinary.uploader.upload(file_path, **upload_params)
        logger.info("Image uploaded to Cloudinary", public_id=result.get("public_id"), url=result.get("secure_url"))
        return result

    @staticmethod
    def upload_audio(
        file_path: str,
        public_id: Optional[str] = None,
        folder: str = "videogen/audio",
        **kwargs,
    ) -> Dict[str, Any]:
        upload_params = {
            "resource_type": "video",
            "folder": folder,
            "use_filename": True,
            "unique_filename": True,
            "overwrite": False,
        }
        if public_id:
            upload_params["public_id"] = public_id
        upload_params.update(kwargs)

        logger.info("Uploading audio to Cloudinary", public_id=public_id, folder=folder)
        result = cloudinary.uploader.upload(file_path, **upload_params)
        logger.info("Audio uploaded to Cloudinary", public_id=result.get("public_id"), url=result.get("secure_url"))
        return result

    @staticmethod
    def get_video_url(
        public_id: str,
        transformations: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> str:
        if transformations is None:
            transformations = [
                {"width": 1080, "height": 1920, "crop": "fill", "gravity": "auto", "aspect_ratio": "9:16"},
                {"quality": "auto", "fetch_format": "auto"},
            ]
        url, _ = cloudinary_url(public_id, resource_type="video", transformation=transformations, **kwargs)
        return url

    @staticmethod
    def get_thumbnail_url(
        public_id: str,
        transformations: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> str:
        if transformations is None:
            transformations = [
                {"width": 1080, "height": 1920, "crop": "fill", "gravity": "auto", "aspect_ratio": "9:16"},
                {"quality": "auto", "fetch_format": "auto"},
                {"format": "jpg"},
            ]
        url, _ = cloudinary_url(public_id, resource_type="video", transformation=transformations, **kwargs)
        return url

    @staticmethod
    def get_watermarked_video_url(
        public_id: str,
        watermark_text: str = "VideoGen AI",
        transformations: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> str:
        if transformations is None:
            transformations = [
                {"width": 1080, "height": 1920, "crop": "fill", "gravity": "auto", "aspect_ratio": "9:16"},
                {"quality": "auto", "fetch_format": "auto"},
                {
                    "overlay": {
                        "font_family": "Arial",
                        "font_size": 60,
                        "font_weight": "bold",
                        "text": watermark_text,
                        "color": "white",
                        "opacity": 30,
                    },
                    "gravity": "south_east",
                    "x": 20,
                    "y": 20,
                },
            ]
        url, _ = cloudinary_url(public_id, resource_type="video", transformation=transformations, **kwargs)
        return url

    @staticmethod
    def get_delivery_url(
        public_id: str,
        resource_type: str = "video",
        transformations: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> str:
        url, _ = cloudinary_url(public_id, resource_type=resource_type, transformation=transformations, **kwargs)
        return url

    @staticmethod
    def delete_resource(public_id: str, resource_type: str = "video") -> Dict[str, Any]:
        logger.info("Deleting resource from Cloudinary", public_id=public_id, resource_type=resource_type)
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        logger.info("Resource deleted from Cloudinary", public_id=public_id, result=result)
        return result

    @staticmethod
    def get_resource_info(public_id: str, resource_type: str = "video") -> Dict[str, Any]:
        result = cloudinary.api.resource(public_id, resource_type=resource_type)
        return result

    @staticmethod
    def list_resources(
        resource_type: str = "video",
        prefix: str = "videogen/",
        max_results: int = 100,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        result = cloudinary.api.resources(
            resource_type=resource_type,
            prefix=prefix,
            max_results=max_results,
            **kwargs,
        )
        return result.get("resources", [])

    @staticmethod
    def create_upload_preset(
        name: str,
        folder: str = "videogen/uploads",
        allowed_formats: Optional[List[str]] = None,
        transformation: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        preset_params = {
            "name": name,
            "folder": folder,
            "unsigned": True,
            "resource_type": "video",
        }
        if allowed_formats:
            preset_params["allowed_formats"] = allowed_formats
        if transformation:
            preset_params["transformation"] = transformation

        result = cloudinary.api.create_upload_preset(**preset_params)
        return result


cloudinary_service = CloudinaryService()