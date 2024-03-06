import azure.functions as func
import azure.durable_functions as df
from PIL import Image, ImageDraw, ImageFont

# Initializing a Durable Functions app with HTTP authentication level set to ANONYMOUS
myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@myApp.route(route="orchestrators/{functionName}")
@myApp.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client):
    function_name = req.route_params.get('functionName')
    instance_id = await client.start_new(function_name)
    response = client.create_check_status_response(req, instance_id)
    return response

@myApp.orchestration_trigger(context_name="context")
def image_processing_orchestrator(context):
    initial_image = "/Users/Umay/Desktop/resizetest.jpg"  # Adjust the path as needed
    resized_image = yield context.call_activity("ResizeImage", initial_image)
    grayscale_image = yield context.call_activity("GrayscaleImage", resized_image)
    final_image = yield context.call_activity("WatermarkImage", grayscale_image)
    return final_image

@myApp.activity_trigger(input_name="image_path")
def ResizeImage(image_path: str):
    new_size = (1024, 768)  # New size
    resized_image_path = image_path.replace(".jpg", "_resized.jpg")
    image = Image.open(image_path)
    resized_image = image.resize(new_size)
    resized_image.save(resized_image_path)
    return resized_image_path

@myApp.activity_trigger(input_name="image_path")
def GrayscaleImage(image_path: str):
    grayscale_image_path = image_path.replace("_resized.jpg", "_grayscale.jpg")
    image = Image.open(image_path)
    grayscale_image = image.convert("L")
    grayscale_image.save(grayscale_image_path)
    return grayscale_image_path

@myApp.activity_trigger(input_name="image_path")
def WatermarkImage(image_path: str):
    watermarked_image_path = image_path.replace("_grayscale.jpg", "_watermarked.jpg")
    image = Image.open(image_path)
    watermark_text = "© Your Watermark"
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()  # Consider using a specific font here
    text_width, text_height = draw.textsize(watermark_text, font)
    position = (image.width - text_width, image.height - text_height)  # Bottom right corner
    draw.text(position, watermark_text, (255, 255, 255), font=font)
    image.save(watermarked_image_path)
    return watermarked_image_path
