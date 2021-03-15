# MDP_Grp6_Algorithms

Repository for all code related to MDP Group 6's Maze Navigation and Image Recognition Algorithms.

The team will implement all algorithms on a separate computer and communicate with the RPI through TCP/IP Socket.

## Setup & Requirements

#### 1. Choose a variation of Pytorch to install:

If you have a CPU

```
pip install torch==1.7.1+cpu torchvision==0.8.2+cpu -f https://download.pytorch.org/whl/torch_stable.html
```

If you have a CUDA GPU

```
pip install torch===1.7.1+cu110 torchvision===0.8.2+cu110 -f https://download.pytorch.org/whl/torch_stable.html
```

#### 2. Install detecto & tqdm

```
pip install detecto tqdm
```

## Run the project

To run the simulation:

```
python simulation.py
```

To run the Fastest path algorithm with the RPI:

```
python actual_algorithm_run.py -tt=fp

OR

python actual_algorithm_run.py --task-type=fp
```

To run the exploration algorithm with the RPI:

```
python actual_algorithm_run.py -tt=exp

OR

python actual_algorithm_run.py --task-type=exp
```

To run the image recognition service for the image recognition exploration (**Required for Image Recognition
Exploration**):

```
python image_recognition_service.py
```