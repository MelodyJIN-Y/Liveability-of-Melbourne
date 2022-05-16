<div id="top"></div>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![GNU License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
<h1 align="center">The Liveability of Melbourne </h1>
  <p align="center">
    <br />
    <a href="https://github.com/MelodyJIN-Y/Liveability-of-Melbourne">View Demo</a>  
  </p>
</div>

<!-- ABOUT THE PROJECT -->
## About The Project
This is a group project for COMP90024 Cluster and Cloud Computing (Semester 1, 2022), The University of Melbourne. 

YouTube videos: https://www.youtube.com/playlist?list=PLhue6Y7TCUD3a12XNekhmNJNRnn6a2gsQ

[![Product Name Screen Shot][product-screenshot]](https://example.com)

### Team members: 
* Xinyi Jin (Melody)  [![LinkedIn][linkedin-shield]][linkedin-url-Melody]

* [Yan Ying (Eliza)](yying4@student.unimelb.edu.au)
 
* [Xinhao Hao (Budd)](xinhaoh1@student.unimelb.edu.au)

* [Liqin Zhang](liqizhang@student.unimelb.edu.au)

<p align="right">(<a href="#top">back to top</a>)</p>


### Built With

* [Melbourne Research Cloud](https://dashboard.cloud.unimelb.edu.au)
* [AURIN](https://portal.aurin.org.au)
* [Ansible](https://www.ansible.com)
* [Docker](https://www.docker.com)
* [Twitter API](https://dev.twitter.com/)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* Twitter developer account 

  list your twitter developer account tokens and named it as . See the format in `.json`
* MRC access 
  
    * download the cloud file and named it as `clouds.yaml`. Put the file to `host_vars`. This file will be used by OpenStack tools as a source of configuration on how to connect to a cloud. See the example in `clouds-example.yaml`
  
    * get the openRC file for the project. For example, we are group 18 and our file is called `unimelb-COMP90024-2022-grp-18-openrc.sh`

### Installation

Clone the repo
   ```sh
   git clone https://github.com/MelodyJIN-Y/Liveability-of-Melbourne.git
   ```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

### System deployment 
We use Ansible and Docker to configure and deploy the system. The foder `Ansible` contains all the deployment files. The entire system can be deployed with one single playbook `entire_process.yaml` and the file `run-entire-process.sh`

We also provide a step-by-step version to deploy the system for testing and illustration purpose. The `deployment-intermediate-step` folder contains breakdown steps to configure and deploy the system. We use dynamic inventory methods in the depoloyment thus no inventory files are provided. We need to run dynamic inventory in each intermediate deployment step to get the ip and group inforamtion.  
* #### Option1: one-step deployment 

  ```sh
  ./run-entire-process.sh
  ```
* #### Option2: step-by-step deployment 
  1. launch and configure instance: 
  
      realted playbook: `s1-create-instances.yaml`
    
      ```sh
      ./s1-run.sh
      ```
  2. set up CouchDB and CouchDB cluster  
      
      realted playbook: `s2-setup-couchdb.yaml`
    
      ```sh
      ./s2-run.sh
      ```
  3. deploy backend applications  
      
      realted playbook: `s3-deploy-backend.yaml`
    
      ```sh
      ./s3-run.sh
      ```
  4. deploy front-end applications  
      
      realted playbook: `s4-deploy-frontend.yaml`
    
      ```sh
      ./s4-run.sh
      ```
### Back-end

### Front-end 

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the GNU License. See `LICENSE` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Project Link: [https://github.com/MelodyJIN-Y/Liveability-of-Melbourne](https://github.com/MelodyJIN-Y/Liveability-of-Melbourne) 
* Xinyi Jin (Melody): xinyij4@student.unimelb.edu.au
* Yan Ying (Eliza): yying4@student.unimelb.edu.au
* Xinhao Hao (Budd): xinhaoh1@student.unimelb.edu.au
* Liqin Zhang: liqizhang@student.unimelb.edu.au


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [README template](https://github.com/othneildrew/Best-README-Template)
<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/MelodyJIN-Y/Liveability-of-Melbourne.svg?style=for-the-badge
[contributors-url]: https://github.com//MelodyJIN-Y/Liveability-of-Melbourne/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/MelodyJIN-Y/Liveability-of-Melbourne.svg?style=for-the-badge
[forks-url]: https://github.com//MelodyJIN-Y/Liveability-of-Melbourne/network/members
[license-shield]: https://img.shields.io/github/license/MelodyJIN-Y/Liveability-of-Melbourne.svg?style=for-the-badge
[license-url]: https://github.com/MelodyJIN-Y/Liveability-of-Melbourne/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url-Melody]: https://www.linkedin.com/in/melody-jin/
[video-shield]: https://img.shields.io/youtube/channel/views/UCLdeGdBHXeT1GqU83WmMy0w?style=social
[product-screenshot]: images/webpage.png
