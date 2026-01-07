PROMPT="I have an image https://ik.imagekit.io/2pej2semh/Actual%20ImageXXXXXXXXXXXXX.png?updatedAt=1762759815408 in my account. Remove its background and save it as 'actual_image_no_bg.png'?"

dotenv run -- python -m src.agent "{\"prompt\": \"$PROMPT\"}"


# dotenv run -- python -m src.agent '{"prompt": "How much bandwidth have i consumed last two month?"}'
# dotenv run -- python -m src.agent '{"prompt": "How to remove a background from an image cost effectively?"}'
# dotenv run -- python -m src.agent '{"prompt": "I have an image https://ik.imagekit.io/2pej2semh/Actual%20Image.png?updatedAt=1762759815408 in my account. How can I remove the background from this image using ImageKit?"}'