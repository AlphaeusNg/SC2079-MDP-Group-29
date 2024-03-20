# Code to update model to fit newest yolo version

# Error Message
'''
WARNING  'ultralytics.yolo.v8' is deprecated since '8.0.136' and will be removed in '8.1.0'. Please use 'ultralytics.models.yolo' instead.
WARNING  'ultralytics.yolo.utils' is deprecated since '8.0.136' and will be removed in '8.1.0'. Please use 'ultralytics.utils' instead.
Note this warning may be related to loading older models. You can update your model to current structure with:
    import torch
    ckpt = torch.load("model.pt")  # applies to both official and custom models
    torch.save(ckpt, "updated-model.pt")
'''

import torch
ckpt = torch.load("best.pt", map_location=torch.device('cpu'))  # applies to both official and custom models
torch.save(ckpt, "updated-best.pt")