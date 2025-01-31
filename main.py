#!/usr/bin/env python3
"""Main file for the 3D graphics project."""
import sys
import warnings
import signal
import numpy as np
import matplotlib.pyplot as plt
from transformers import world_to_screen, rotate_y
from load_world import world1

SUPPRESS_WARNINGS = True
WALKING_SPEED = 0.5 # units per input
TURNING_SPEED = 10 # deg per input
FOCAL_LENGTH = 2
SCREEN_X_SIZE = 16/9

SCREEN_Y_SIZE = 1

def close_event(event): # pylint: disable=unused-argument
    """Handle the GUI close event."""
    print('\n[!] Exiting...')
    sys.exit(0)

def signal_handler(sig, frame): # pylint: disable=unused-argument
    """Handle the CTRL+C signal."""
    print('\n[!] Exiting...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main(): # pylint: disable=too-many-statements
    """Main function."""
    if SUPPRESS_WARNINGS:
        warnings.filterwarnings('ignore')

    # set initial camera position
    camera_origin = np.array([0, 0.5, 0, 1], dtype=np.float64)
    camera_yaw = 0
    camera_pitch = 0

    world = world1()


    walking_deltas = {
        'w': np.array([0, 0, WALKING_SPEED, 1], dtype=np.float64).T,
        's': np.array([0, 0, -WALKING_SPEED, 1], dtype=np.float64).T,
        'a': np.array([-WALKING_SPEED, 0, 0, 1], dtype=np.float64).T,
        'd': np.array([WALKING_SPEED, 0, 0, 1], dtype=np.float64).T
    }

    # print instructions

    print('When you are ready, a matplotlib window will open.')
    print('You will enter movement commands in this terminal window, ' +
          'and see the scene in the matplotlib window.')
    print()
    print('When the matplotlib window opens, set up the windows so both are visible.')
    print('!!! sometimes matplotlib is finicky and you have to enter a ' +
          'few movement commands for it to work properly !!!')
    print()
    print('Press enter to continue...')
    input()

    # initialize matplotlib screen
    plt.ion()
    fig = plt.figure()
    fig.canvas.mpl_connect('close_event', close_event)
    ax = fig.add_subplot(111) # pylint: disable=invalid-name
    # get rid of the numbers on the axes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim([-SCREEN_X_SIZE / 2, SCREEN_X_SIZE / 2])
    ax.set_ylim([-SCREEN_Y_SIZE / 2, SCREEN_Y_SIZE / 2])
    ax.set_aspect('equal')
    plt.tight_layout()
    line = ax.plot([0], [0], '-')[0]


    print('Enter characters to move the camera:')
    print('\twasd to move forward, backward, left, right')
    print('\tqe to turn left, right')
    print('\trf to look up, down')
    print()
    print('Press CTRL+C to exit')
    while True:
        # get the world to screen transformation
        world_to_screen_transform = world_to_screen(camera_pitch, \
            camera_yaw, camera_origin, FOCAL_LENGTH)

        # transform the world to screen coordinates
        homogenous_screen_coords = world_to_screen_transform @ world
        # find all the points that are behind the camera and set them to nan
        behind_camera = homogenous_screen_coords[2] < 0
        homogenous_screen_coords[:, behind_camera] = np.nan
        screen_coords = homogenous_screen_coords[:2] / homogenous_screen_coords[2]

        # draw the cube
        line.set_xdata(screen_coords[0, :])
        line.set_ydata(screen_coords[1, :])
        fig.canvas.draw()
        fig.canvas.flush_events()

        # handle events
        user_input = input('Enter a command:')
        if user_input == '':
            continue
        user_input = user_input[-1]

        if user_input in walking_deltas:
            camera_origin += rotate_y(-camera_yaw) @ walking_deltas[user_input]

        elif user_input == 'q':
            camera_yaw += (np.pi / 180) * TURNING_SPEED
        elif user_input == 'e':
            camera_yaw -= (np.pi / 180) * TURNING_SPEED
        elif user_input == 'r':
            camera_pitch += (np.pi / 180) * TURNING_SPEED
        elif user_input == 'f':
            camera_pitch -= (np.pi / 180) * TURNING_SPEED

if __name__ == '__main__':
    main()
