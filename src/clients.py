import os
from imagekitio import AsyncImageKit

CLIENT = AsyncImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
)
