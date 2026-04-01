Canvas / Discord Group Number
53380_01

Git SHA:
90b2dd51dbbeb7acf740a4815cfa0d5ec428a528

Team Lead
Dylan Dang

Team Members
Dev Shroff ds58947 @devbshroff
Estimated Hours: 14h Total Hours: 19h

Franklin Wright fsw273 @franklinwright
Estimated Hours: 12h Total Hours: 19h

Dylan Dang dad4364 @dylan-dang
Estimated Hours: 17h Total Hours: 19h

Bob Zhu bz5283 @zhubob3
Estimated Hours: 17h Total Hours: 19h

Project Website
https://railreach.me/

Postman:
https://documenter.getpostman.com/view/52516897/2sBXcDHh5J

Proposal

Canvas / Discord group number: 53380_01

Names of the team members: Dev Shroff, Franklin Wright, Dylan Dang, Bob Zhu

Name of the project: RailReach

The proposed project: With our project, we aim to improve awareness about trains as a mode of transport for underserved communities in America. American trains are used primarily by people of lower socioeconomic classes, when they are used as a mode of transportation, even though they are better for the environment, and could very well be faster than cars or other modes of transportation, given the right investment at a national level. To raise awareness for this issue and potentially influence funding efforts to bring more money into train infrastructure, we will make a site showing three models of train stations, train routes, and the regions they cover. This will hopefully have the effect of having people be more aware of how they can use trains, even if they are not the typical demographic that does so, so that more funding can follow the increase in ridership. We are essentially trying to get people to vote with their choice of transport, because if more people ride trains, they will get more funding, and the people who do have to use them, specifically underserved communities, will have better infrastructure, schedules, and an overall experience using public transport.

At least 3 data sources  
[https://amtraker.com/](https://amtraker.com/)  
[https://www.transit.dot.gov/ntd/ntd-data](https://www.transit.dot.gov/ntd/ntd-data)  
[Amtrak Routes & Destinations](https://www.amtrak.com/train-routes)  
[Travel Planning Map | Amtrak](https://www.amtrak.com/plan-your-trip.html)  
[https://www.census.gov/data/developers/data-sets/acs-5year.html](https://www.census.gov/data/developers/data-sets/acs-5year.html)

We will get information on the train routes from the Amtrak Routes site, which also gives us images of trains and train stations, embedded maps, which stations routes cover, and more.

We will get the information on train stations from [amtraker.com](http://amtrak.com), this will be the source we programmatically scrape with Restful API.

We will get more information on the regions that the trains serve via the Census API. This includes more information about demographics and other things about the people that the trains in the region serve.

Models:

1. Amtrak Train Stations
2. Amtrak Routes
3. Regions

Model 1: Amtrak Train Stations \~2000 instances

- Attributes
  - Station names
  - Station code
  - Station address
  - Station time zone
  - Station description
  - Station hours
  - Stations in the vicinity
  - Points of interest near station
  - Main connected destinations
  - Routes served count
- Media
  - Interactive map
  - Images of the station
- Connections
  - Which routes this station connects
  - Which regions this station is in

Model 2: Amtrak Routes \~40 instances

- Attributes
  - Route name
  - Major stops
  - Short description of the route
  - Menu
  - Number of hours to travel the route
  - Stations served count
- Media
  - Routes on an interactive map
  - Images of the area the Route covers
- Connections
  - Which stations this route connects
  - Which regions this route crosses

Model 3: Regions \~50 instances

- Attributes
  - Total Population
  - Median Household Income
  - No Vehicle Available
  - Poverty Status
  - Public Transportation to Work
- Media
  - Map of Region
  - Text about Region
  - Images of the area in the Region
- Connections
  - Which stations does this region has
  - Which routes does this region has

Questions:

- What stations and routes can I take to get from Point A to Point B?
- What can I do personally to improve American train infrastructure?
- Why should I care about public transit?
- Which regions should build more train infrastructure?
