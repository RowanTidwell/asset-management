# asset-management

A lightweight production-tracking system inspired by ShotGrid/Flow. Provides a
centralized web API and web UI backed by PostgreSQL, plus a Python desktop
application and CLI that sync with the server. Use it to manage Projects,
Assets, Shots, Tasks, and related metadata, with optional DCC integration for
local tools.

#### Background
I previously worked at a game studio working on some in-depth Shotgrid integration. I'd like to show off that work but its so dependent on Shotgrid and I would rather not spend the small fortune that app costs. So I am doing what any reasonable person would do:  
_Writing the whole full stack web experience myself_

#### Methodology 
I am going to be writing a majority of the code by hand for my own learning journey.  
I will be using copilot from time to time when my free credits allow and its on a topic I am unfamiliar with. I will go back and reformat and organize that code by hand so I learn that topic and hopefully rely on my on skills to maintain it. The initial check in contains a majority AI written code since I am unfamiliar with backend server authoring. Though I combed through every line so I could absorb that information for myself.

## Components

### Core
&nbsp;This is where code that can be used between the apps lives. My primary goal for this is to hold constants and other code completion types.

### Backend
&nbsp;Server stuff and API

### Web App
&nbsp;This app will most likely end up running with the backend but primarily be GUI for the browser.

### Desktop App + CLI
&nbsp;This app is where the core content creation and asset browsing components will live. It will discover the app plugins as defined below.

### Desktop DCC App Plugins
&nbsp;To best suit a studios needs, individual modules will be created to support different DCC apps. The ones I had made in the past were Maya, Perforce, Unreal, Photoshop etc.
