# USD Mercury
USD Mercury is an innovative tool designed to streamline the setup of a complete VFX/CGI pipeline leveraging Universal Scene Description (USD). This solution is ideal for both individual artists and collaborative group projects. The core of USD Mercury is developed in Python, incorporating various APIs to ensure seamless integration with different Digital Content Creation tools (DCCs).

## Features
-   Unified Pipeline: Leverage the power of USD to unify your project's pipeline.
-   Extensible Integration: Compatible with multiple DCCs via API integration.
-   User-Friendly Interface: GUI developed in PySide2/PyQt5 for ease of use.
-   Project Tracking: Initially using SQLite for project tracking, with plans to migrate to Shotgun API for enhanced project management capabilities.

## Overview
### USD Asset Creation
The assets generated by the plugin adhere to the structuring guidelines set forth by the ASWF (Academy Software Foundation's Universal Scene Description Working Group). For detailed information on these guidelines, please refer to the ASWF Asset Structure Guideline.

In addition to complying with ASWF standards, my approach integrates methodologies from the Alab scene by Animal Logic. Specifically, I’ve adopted the Alab methodology of Entities and Fragments, which influences the asset construction logic and folder management practices. Further details on this methodology can be found in the Alab AnimalLogic Documentation.
#### Modelling Department
In the Asset Modeling Department, Autodesk Maya serves as the primary modeling Digital Content Creation (DCC) tool. The plugin enhances Maya's capabilities by structuring outputs using the geo variant set logic. This logic facilitates the conversion of Maya's internal geometric data into a format readable by USD. Key conversions performed by the plugin include:

-   Extent: This defines the axis-aligned bounding box for the mesh, which is used for spatial partitioning, culling, and other optimizations. It's defined by the minimum and maximum corners.
-   Face Vertex Counts: This is an array where each element specifies the number of vertices that make up each face of the mesh. In this file, each face has 4 vertices, which typically means the -    mesh is composed of quads.
-   Face Vertex Indices: This array defines the indices into the points array for each vertex of each face, essentially which points are used to define each face.
-   Normals.
-   3D points: This array defines the 3D coordinates for each vertex of the mesh.
-   Display Color: This is a color array that specifies the color to be used when displaying the mesh in a viewer
-   Texture Coordinates:  This array defines the texture coordinates for the mesh, necessary for applying textures.
-   Texture Indices: This array of indices maps the texture coordinates to the mesh vertices.

Additionally, the plugin is responsible for constructing the main hierarchy of the asset. It defines the root primitive, class inheritance, and sets the purpose for render and proxy meshes. It also manages variant sets, including the creation of variants and setting default variants.

By leveraging intermediate USD files (lightweight files that reference heavier geometric data in .usdc or .usda formats), the plugin allows users to pin or unpin the current version of the payload that each asset variant uses, overriding the latest publication. This feature enhances version control and scene management within the production pipeline.

A video of the functioning process of the modelling department can be found on my Vimeo Page: [USD Mercury Pipeline: Asset Creation Pt. 1 - Modelling](https://vimeo.com/938380663?share=copy)


This is the first prototype of the project (MVP) and will be develop further to include the following:
*This is a live list and will be upgraded in time.*

- USD Asset Creation:
    - Ability to work on assets over different DCCs (Maya, Houdini, Painter, SpeedTree on the roadmap).
    - Asset types, assemblies and groups for organization. 
    - Ability to customize the departments intervening in the asset creation process including: 
        - Modelling department
        - Shading department
        - Rigging department
        - Fx department
        - Cfx department
        - Lighting department
    - Variant Sets and Variant publicaction system for all departments and scene management system with versioning with Tasks for organization purposes.
    - Texture export automatization and basic shader building for both MaterialX and Arnold usd. 
    - Template generation for LookDev Scenes, Turntable and render automatization for each step of the Asset Construction.
- USD Shot Creation:
    - Manifest quick creation system through libraries of assets. 
    - Ability to work either through departmental or combined logic (for both single and multi users). Including:
        - Manifest Creation
        - Layout department
        - Animation department
        - Fx department
        - Lighting department
        - Compositing department
    - Automatic Sequence and Shot building system for houdini and Nuke. ACES workflow.
    - Ability to set up globals, render settings, AOVs, render layers and general preferences. 
    - Multishot support. 
    - Automatic pre-comp generation after render. 
- USD Pipeline Management:
    - Project Tracking either off-line through database or online using Shotgrid. 
    - Complete folder tracking system and naming convention set up. 
    - User Support for authoring.
    - Version Control and ability to apply overrides.


## Installation

A first version of the complete plug in will be launched soon. 



## Personal learning objectives

- Understand the benefits and implementation of the Universal Scene Description (USD) to streamline VFX/CGI pipelines.
- Investigate bottlenecks in the USD-centric pipelines and the DCCs implementations, for future optimization or workarounds.
- Leverage a unified pipeline across various Digital Content Creation (DCC) tools, enhancing project consistency and collaboration. Implement and combine the different DCCs Python APIs.
- Enhance technical skills in handling complex assets and shots. Solidify naming conventions ideas and folder structures for USD-centric pipelines.
- Gain proficiency in project tracking and management using both SQLite and Shotgun API for larger scale project oversight.
- Develop an understanding of variant sets and their applications in creating versatile and manageable digital assets.
- Explore the creation of automated systems for asset assembly, rendering setups, and version control within a USD-centric environment.


## Contributing

Thank you for your interest in contributing to my project! Here are the guidelines if you wish to participate in the project.

### Prerequisites

- Git installed (See here for installation instructions: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- USD Core Pre-Built for Python (See here for installation: https://developer.nvidia.com/usd)
- Familiarity with Houdini, Nuke, Maya and Painter APIs very much appreciated.
- Familiarity with Python and Pyside2.

### Setting Up for Development

1. Fork the repository by clicking on the 'Fork' button on the top right of this page.
2. Clone your forked repository to your local machine.

### Making Changes

1. Create a new branch
2. Make your changes, add them, and commit them.
3. Push your branch to your fork.
4. Go to the repository on GitHub. You'll see a `Compare & pull request` button. Click on it and submit your pull request with a comprehensive description of your changes.

### Pull Request Guidelines

- Ensure your pull request describes the proposed changes or the issue it resolves.
- Pull requests should be made against the `main` branch.
- Do not include any compiled files in the pull request.
- If relevant, include unit tests or updates to existing tests with your changes.
- Ensure all tests pass locally.

## License
This project is licensed under the GNU GPLv3 License - see the [LICENSE](LICENSE.txt) file for details.