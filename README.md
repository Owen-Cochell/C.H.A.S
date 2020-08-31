# Computerised Home Automation System

A modular, privacy driven, home automation system written in Python

# Introduction

Computerised Home Automation System(or CHAS for short) has been a passion project of mine for quite some time now.

I often found the concepts of home assistants to be fascinating, but I have always disliked the amount of data they 
gather, and the privacy risks that are involved with them.

So, I figured I should create and design my own Home Assistant, with modularity, efficiency, and most importantly,
privacy as the main goals. I also started the project to help myself get a better understanding of networking,
API design, voice recognition, natural language processing, artificial intelligence, and so on.

# Features

CHAS offers the following features:

 - Custom socket server for server to node communication
 - Wrappers for popular voice recognition engines
 - WAV file reader and writer that allows streaming audio over a network
 - Plugin system for adding extra functionality to CHAS
 - Personality system/chatbot framework for giving CHAS a personality
 - Custom nCurses wrappings for front end development
 - Espeak wrappers for voice synthesis
 
 The CHAS front end is entirely text based, meaning that CHAS can run very well on slow, old, or embedded systems.
 You can interact with CHAS via voice or text.
 
 # CHAS Development
 
 I started working on CHAS when I was very inexperienced, so the general stability of CHAS can be lackluster,
 and some of the features are clunky. As time goes on, I will be continuously fixing and adding features to CHAS,
 so it can be a coherent project.
 
 # Running CHAS
 
 CHAS is designed entirely for Linux. I have been able to get CHAS working on windows machines, but the installation
 process is very complicated, and stability and performance suffered because of it. Linux will be the main CHAS platform
 for the foreseeable future.
 
 ## Instillation
    
Install SpeechRecognition package:

> pip install SpeechRecognition

Install pyaudio package:

> 'sudo apt-get install python3-pyaudio'
> 'sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0'
> 'pip install pyaudio'

Install Espeak:

> apt install espeak

Install Python Pocketsphinx:

> sudo apt-get install python3 python3-all-dev python3-pip build-essential swig git libpulse-dev libasound2-dev
> pip install pocketsphinx

You can install these dependencies on any distro, just substitute 'apt' for your distros package manager.

You will need python to run CHAS. Find out how to do that [here](https://www.python.org/downloads/).

After this, clone this repository to get the CHAS files. 

## Starting CHAS

CHAS is split up into two directories, one for the server and one for the client.

Their only needs to be one server instance on your network. There can be as many clients as you want.
The idea is that you put a client into a room that needs CHAS functionality.

To start the server, you must start mainFile.py. You can do this like so:

> python3.7 mainFile.py

You can start the clients the same way, just check the client directory.
Be sure to check the 'settings.py' file in each directory, as it contains important configuration info.

## Example

Lets say you have one server and three clients on your network. Lets also say that a user gives a command to the client.

If the client dose not have a handler that can handle the command, then it will send the command to the server. If the
server can handle the command, it will send a response back. If not, it will tell the client that the command 
can't be handled.

This command is then sent to the personality of the client
(Which can be configured to query the personality of the server instead of the client), and will then send the response 
back to the human in text form or speech, depending on how the user interacted with the client.

This principle allows your clients to be very lightweight, as you can put all of your functionality in the server.
This also works well for synchronising the state between clients, and mass sending info to each client.

# Documentation

One of the biggest problems with CHAS is the lack of documentation. At some point I will be creating and hosting
docs that will explain all of the CHAS features, and how to use them effectively.

The scope for CHAS is very big, so this task will take quite some time.

# TODO:

 - Add wrappings to ffmpeg, so we can read other types of audio files
 - Overhaul the plugin system - Decorator based registration, decide between strict and fluid handling
 - Make code comments Sphinx compliant
 - Fix or remove old/obsolete code(netools especially)
 - Re-organise the project - Our current structure is confusing and strange
 - Add rules for contributors
 - Add modular voice synthesizer support - Change the synth at will during runtime
 - Add tone synthesiser support - So chas can generate basic tones and chords 
 - Fix included plugins - The music plugin is very cryptic and poorly designed
 - Add custom exceptions and error handling
 - Network streamer could be redone to be more efficient/concise
 - Many many more!
 
 # Conclusion
 
 CHAS has been an on and off project for a very long time. It will likely remain this way, with small bursts 
 of improvement/change. I would like CHAS to eventually become a viable solution to home automation, providing a
 privacy-driven, open source solution for your home.
 
 CHAS is a huge work in progress, meaning that any part of CHAS can suddenly change with no warning.
 
 Thank you for reading!