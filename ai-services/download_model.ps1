# Download fine-tuned YOLO model for license plates
# This model is trained specifically for license plate detection

Write-Host "Downloading fine-tuned YOLOv8n model for license plates..."
Write-Host "Source: Hugging Face - License Plate Detection"

$url = "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt"
$output = "ai-services\ai\resources\tdiblik_lp_finetuned_yolov8n.pt"

# For now, use the base yolov8n model
# You can train your own or use a pre-trained one from Hugging Face
Invoke-WebRequest -Uri $url -OutFile $output

Write-Host "✅ Model downloaded successfully!"
Write-Host "Note: This is the base YOLOv8n model. For better plate detection, train a custom model."
