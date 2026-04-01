import { useEffect } from "react";
import { Route, Routes, useLocation } from "react-router-dom";
import trainCityImg from "./assets/wal_172619-city-7576853_1280.jpg";
import { DotBackground } from "./components/bg.tsx";
import { MarqueeDemo } from "./components/marquee.tsx";
import { DockDemo } from "./components/navigation.tsx";
import "./index.css";
import { AboutPage } from "./pages/AboutPage.tsx";
import { RegionInstancePage } from "./pages/RegionInstancePage.tsx";
import { RegionsPage } from "./pages/RegionsPage.tsx";
import { RouteInstancePage } from "./pages/RouteInstancePage.tsx";
import { RoutesPage } from "./pages/RoutesPage.tsx";
import { SearchPage } from "./pages/SearchPage.tsx";
import { StationInstancePage } from "./pages/StationInstancePage.tsx";
import { StationsPage } from "./pages/StationsPage.tsx";

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  return null;
}

function App() {
  return (
    <>
      <ScrollToTop />
      <Routes>
        <Route
          path="/"
          element={
            <div className="relative flex min-h-screen flex-col items-center overflow-x-hidden">
              <DotBackground>
                <h1 className="relative z-10 font-bold text-4xl tracking-tight sm:text-6xl">
                  RailReach
                </h1>
              </DotBackground>
              <MarqueeDemo />
              <div className="z-50 mt-4 mb-6 w-full max-w-6xl shrink overflow-y-auto px-4">
                <p className="text-gray-500 text-lg dark:text-gray-400">
                  We aim to improve awareness about trains as a mode of
                  transport for underserved communities in America. American
                  trains are used primarily by people of lower socioeconomic
                  classes, when they are used as a mode of transportation, even
                  though they are better for the environment, and could very
                  well be faster than cars or other modes of transportation,
                  given the right investment at a national level. To raise
                  awareness for this issue and potentially influence funding
                  efforts to bring more money into train infrastructure, we want
                  to show you three train stations, train routes, and the
                  regions they cover. This will hopefully have the effect of
                  having people be more aware of how they can use trains, even
                  if they are not the typical demographic that does so, so that
                  more funding can follow the increase in ridership. We are
                  essentially trying to get people to vote with their choice of
                  transport, because if more people ride trains, they will get
                  more funding, and the people who do have to use them,
                  specifically underserved communities, will have better
                  infrastructure, schedules, and an overall experience using
                  public transport.{" "}
                </p>
                <img
                  src={trainCityImg}
                  alt="City train"
                  className="mt-4 w-full rounded-lg"
                />
              </div>
            </div>
          }
        />
        <Route path="/stations" element={<StationsPage />} />
        <Route path="/stations/:id" element={<StationInstancePage />} />
        <Route path="/routes" element={<RoutesPage />} />
        <Route path="/routes/:id" element={<RouteInstancePage />} />
        <Route path="/regions" element={<RegionsPage />} />
        <Route path="/regions/:id" element={<RegionInstancePage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/about" element={<AboutPage />} />
      </Routes>
      <DockDemo />
    </>
  );
}

export default App;
