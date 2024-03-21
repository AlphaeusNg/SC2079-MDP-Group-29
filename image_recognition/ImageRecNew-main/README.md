# Setup

1. Clone and create .env file within root directory
   ```
    git clone https://github.com/SC2079-MDP/ImageRec.git
   ```
3. Ask Wei Kang for API Key from roboflow to download images, or simply go to Training folder, and access Colab notebook.
4. Key in the API Key for Roboflow to download images into .env file.

```
ROBOFLOW_API_KEY=<THE API KEY>
```

4. Run the following command to install dependencies:

```
pip install -r requirements.txt
```

## Directories

- **ImageRec** - Main project folder
    - **Download Dataset**: Contains notebook to download dataset from roboflow as YoloV8 Dataset
    - **Training**: Contains notebook to train YoloV8 Model
    - **Runs**: Contains results of predictions after predicting, as well as final stitched images
    - **YoloV8 Inference Server**: Contains code for the ImageZMQ Server to make predictions on PC using model weights after training + best weights from training
    - **example.env**: Example env file for you to create your own env file.
    - **requirements.txt**: requirements of the imageZMQ Server


    
