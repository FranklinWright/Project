import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { StationInstancePage } from "./StationInstancePage";

const mockUseStationQuery = jest.fn();

jest.mock("@/lib/queries", () => ({
  useStationQuery: () => mockUseStationQuery(),
}));

const mockStation = {
  id: 1,
  name: "Austin Station",
  code: "AUS",
  imageUrl: "https://example.com/aus.jpg",
  linkedRoutes: [
    {
      id: 1,
      name: "Texas Eagle",
      imageUrl: "https://example.com/texas-eagle.jpg",
      regionsSpanned: ["TX"],
      majorStops: ["Austin"],
      menu: ["Snacks"],
      stationsServed: 1,
      travelTimeInHours: "32h",
    },
  ],
  linkedRegion: {
    id: 1,
    name: "Texas",
    code: "TX",
    imageUrl: "https://example.com/tx.jpg",
  },
};

function renderStationPage(path = "/stations/AUS") {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/stations/:id" element={<StationInstancePage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("StationInstancePage", () => {
  beforeEach(() => {
    mockUseStationQuery.mockReturnValue({ data: mockStation });
  });

  it("renders station details for a valid station code", () => {
    renderStationPage();

    expect(
      screen.getByRole("heading", { name: /Austin Station/i, level: 1 }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Servicing Routes", level: 2 }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Region", level: 2 }),
    ).toBeInTheDocument();
  });

  it("exposes links to related route and region pages", () => {
    const { container } = renderStationPage();

    const routeLink = container.querySelector('a[href="/routes/texas-eagle"]');
    const regionLink = container.querySelector('a[href="/regions/TX"]');

    expect(routeLink).toBeTruthy();
    expect(regionLink).toBeTruthy();
  });

  it("renders not found state when query returns no station", () => {
    mockUseStationQuery.mockReturnValue({ data: undefined });

    renderStationPage("/stations/UNKNOWN");

    expect(screen.getByText("Station not found.")).toBeInTheDocument();
  });
});
