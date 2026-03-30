Purpose/Motivation: We aim to raise awareness of trains as a mode of transportation for underserved communities in America. American trains are used primarily by people of lower socioeconomic classes when they are used as a mode of transportation, even though they are better for the environment and could very well be faster than cars or other modes of transportation, given the right national-level investment. To raise awareness of this issue and potentially influence funding efforts to expand train infrastructure, we want to show you three train stations, their routes, and the regions they serve. This will hopefully have the effect of having people be more aware of how they can use trains, even if they are not the typical demographic that does so, so that more funding can follow the increase in ridership. We are essentially trying to get people to vote with their choice of transport, because if more people ride trains, they will get more funding, and the people who do have to use them, specifically underserved communities, will have better infrastructure, schedules, and an overall experience using public transport. 

User Stories: The following are the user stories we received and how we addressed them.

1. User Stories: Adding Total Stations and Routes to Region Instances  
   1. This story is all about adding the total number	of stations and routes in a region to the instance page of that specific region. We accomplished this by extracting the data for these specific numbers and, for now, hardcoding them into the instance pages of the regions.  
2. User Stories: Mobile View  
   1. This story is all about making the site more accessible for mobile device users. We implemented the requirements of this story by going through all the pages on the site and checking that they function as intended on a phone and tablet using the in-built browser tools, as well as on physical mobile devices.  
3. User Stories: Accessibility of Train Stations  
   1. This story is all about adding whether a station is ADA accessible. We implemented this by adding a new box on the station instance pages where we have a boolean value of whether a station is ADA accessible or not.  
4. User Stories: Add a logo  
   1. This story was about adding some form of branding. We have an overall minimal theme, and we are using Lucide Icons throughout for cohesion. We chose the Lucide train icon as our logo, and implemented it by adding it to the tab image.  
5. User Stories: Add Points of Interest Media  
   1. This story is all about adding a picture of at least one point of interest directly in the point of interest card of every station instance. This was accomplished by getting a picture of at least one point of interest near every station and adding it to the instance’s section on points of interest.

Models: We have three models.

1. Stations  
   1. This will eventually cover every Amtrak station in America. Right now, we have three stations as instances of this model: Austin, Sacramento Valley, and Chicago Union. For each station, we have an image of the station, its service hours, the timezone, the number of routes it serves, if it is ADA accessible and the region it is in on the instance card. Once on the instance page we feature the description of the station, the other information shown before, as well as in interactive embedded map of its location, points of interest near the station, nearby stations, connected destinations, official links for more information on the station, the history of the station, and connections to the instance pages of the routes the station services, and the region the station is located in.  
2. Routes  
   1. This will eventually cover every Amtrak route in America. Currently, we have three routes that use this model: Texas Eagle, California Zephyr, and Coast Starlight. For each route, we have an image of the route, its travel time, its dining menu, the stations served, and major stops. We also have links to its route page, description, and YouTube video. We have connected the stations and regions this route passes through.  
3. Regions  
   1. This will soon cover every state in America. Currently, we have three states: Texas, California, and Illinois. For each region, we include an image from the state, an overview of railroad history, population, median household income, no-vehicle access, poverty rate, number of Amtrak stations and routes, and the public transit provider. We have included links to Wikipedia and tourist sites for these states. We have included connections to stations and routes that this region goes through.

Tools: We used different tools.

1. Bun  
   1. We used Bun to serve as the runtime, the bundler, and the server.  
2. TypeScript  
   1. We used this instead of JavaScript as the main language for our code.  
3. Magic UI  
   1. We used this for its wide variety of premade UI components. This includes the dot flickering background, marquees used on the splash, navigation dock, and bento grids used on the model and instance pages.  
4. React  
   1. We used React as the front-end framework to build a responsive UI for the website.  
5. Lucide  
   1. We used Lucide Icons specifically for SVG icons. We used this as icons for our dock, on all the model and instance pages, and as our main site icon in the tab.

Architecture:

frontend/components/

- Shared UI components from Magic UI  
- Navigation bar  
- BentoGrid files for Stations/Routes/Regions model pages  
  - Receive the data arrays from data/, map each to a BentoCard with background image, name, and attributes

frontend/data/

- Data files: export hardcoded data arrays (Station\[\], Route\[\], Region\[\])

frontend/pages/

- Home page  
- About page  
- Model pages import stations/routes/regions and pass them to StationsBentoGrid/RouteBentoGrid/RegionBentoGrid to render all station cards  
- Instance pages have bento boxes for stats/information/text/multimedia

Challenges: We faced a number of challenges; here is how we overcame them.

1. Setting up the bun project:  
   1. For most of us, this was the first time we had interacted with Bun. We were not sure how the commands and modules required worked. We overcame this by reading the Bun documentation. We realised it is a drop-in replacement for Node, and many of the commands are very similar. Once we got that sorted, we understood that the main difference was just replacing npm with bun in the terminal.  
2. Incorporating Magic UI components:  
   1. We had also not used Magic UI before. We know the components could usually be directly dropped in. But we had issues with formatting and making them fit our needs. This was easily overcome by reading the Magic UI documentation.  
3. Managing in-file stored images for display:  
   1. We had some slight issues using images that we stored in the file system on the about page. They were originally not showing up directly and also not raising errors. We eventually found out that we needed to establish proper type checking for TypeScript through a d.ts file, which allowed the images to show up properly.  
4. Instance page connections:  
   1. We had to change the structure of the instance pages at the last minute because we originally just had links, rather than cards, as connections. This broke our original bento box layout, and we had to add new sections to fit those instance cards.  
5. Bento grids (cards) layout and sizing:  
   1. Getting the bento grids to have just the right size needed a lot of tweaking. We experimented with different strategies like static sizing and dynamic sizing. All of this required us to look at the pre-made UI components' code carefully.

Hosting:

* Hosting was set up using a variety of AWS tools:  
  * Identity and Access Management (IAM)  
  * Elastic Container Registry (ECR)  
  * AWS Certificate Manager (ACM)  
  * Amazon CloudFront  
  * AWS Lambda  
* We created a build script to bundle server code and client code entry points to be distributable and portable, so it can be run on AWS Lambda.  
* We created a Dockerfile to encapsulate the built distribution folder on top of the bun layer to run the server code and expose the port.  
* We created an IAM user for the GitLab pipeline and gave it permissions to access our ECR and Lambda functions. Then, we generated an access key to be used in the GitLab pipeline.  
* We set up the GitLab pipeline to lint our project, run the build script, and then build the Docker image. Using masked environment variables, we use the IAM user access key to log into AWS and push and tag our Docker image to our AWS Elastic Container Registry (ECR)  
* We created an AWS Lambda function to reference our ECR and have it so that the GitLab pipeline will update it to run the latest image on the ECR for deployment.  
* We created a domain on Namecheap and created SSL certificates for using Amazon ACM to support HTTPS, and we updated the domain’s CNAME records to verify to Amazon that we own the domain.  
* We created an AWS CloudFront content delivery network (CDN) to serve our website and had it point to our Lambda function.   
* We ensured our CDN used our SSL certificate, and lastly created an ALIAS record in our domain DNS records so it would point to our CDN.

API Documentation:

* We researched industry standards for API pagination to define a consistent response structure.  
* We developed mock endpoints in our server architecture to provide function response examples.  
* We documented all our planned API query parameters that we plan to use so that we can filter and sort in our frontend integration.  
* We added descriptions to all our folders, API routes, and query parameters for each route.