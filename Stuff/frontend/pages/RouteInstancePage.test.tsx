import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { RouteInstancePage } from "./RouteInstancePage";

const mockUseRouteQuery = jest.fn();

jest.mock("@/lib/queries", () => ({
  useRouteQuery: () => mockUseRouteQuery(),
}));

const mockRoute = {
  id: 1,
  name: "Texas Eagle",
  imageUrl: "https://example.com/texas-eagle.jpg",
  linkedStations: [
    {
      id: 1,
      name: "Austin Station",
      code: "AUS",
      imageUrl: "https://example.com/aus.jpg",
    },
  ],
  linkedRegions: [
    {
      id: 1,
      name: "Texas",
      code: "TX",
      imageUrl: "https://example.com/tx.jpg",
    },
  ],
};

function renderRoutePage(path = "/routes/texas-eagle") {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/routes/:id" element={<RouteInstancePage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("RouteInstancePage", () => {
  beforeEach(() => {
    mockUseRouteQuery.mockReturnValue({ data: mockRoute });
  });

  it("renders route details for a valid route id", () => {
    renderRoutePage();

    expect(
      screen.getByRole("heading", { name: /Texas Eagle/i, level: 1 }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Major Stops (Stations)", level: 2 }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Regions Spanned", level: 2 }),
    ).toBeInTheDocument();
  });

  it("exposes links to related station and region pages", () => {
    const { container } = renderRoutePage();

    const stationLink = container.querySelector('a[href="/stations/AUS"]');
    const regionLink = container.querySelector('a[href="/regions/TX"]');

    expect(stationLink).toBeTruthy();
    expect(regionLink).toBeTruthy();
  });

  it("renders not found state when query returns no route", () => {
    mockUseRouteQuery.mockReturnValue({ data: undefined });

    renderRoutePage("/routes/unknown-route");

    expect(screen.getByText("Route not found")).toBeInTheDocument();
  });
});
