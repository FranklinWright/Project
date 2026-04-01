import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { StationsPage } from "./StationsPage";

const mockUseStationsQuery = jest.fn();

jest.mock("@/lib/queries", () => ({
  useStationsQuery: () => mockUseStationsQuery(),
}));

const mockStationsResponse = {
  data: {
    data: [
      {
        id: 1,
        name: "Austin Station",
        code: "AUS",
        imageUrl: "https://example.com/aus.jpg",
      },
      {
        id: 2,
        name: "Dallas Station",
        code: "DAL",
        imageUrl: "https://example.com/dal.jpg",
      },
    ],
    pagination: {
      totalItems: 2,
      totalPages: 1,
      currentPage: 1,
      pageSize: 10,
      hasNextPage: false,
      hasPreviousPage: false,
      links: {
        self: "http://railreach.me/api/stations?page=1&pageSize=10",
        next: null,
        previous: null,
        first: "http://railreach.me/api/stations?page=1&pageSize=10",
        last: "http://railreach.me/api/stations?page=1&pageSize=10",
      },
    },
  },
};

describe("StationsPage", () => {
  beforeEach(() => {
    mockUseStationsQuery.mockReturnValue(mockStationsResponse);
  });

  it("renders heading and instance count", () => {
    render(
      <MemoryRouter>
        <StationsPage />
      </MemoryRouter>,
    );

    expect(
      screen.getByRole("heading", { name: "Stations", level: 1 }),
    ).toBeInTheDocument();
    expect(screen.getByText("Showing 2 of 2 instances")).toBeInTheDocument();
  });

  it("renders links for station instance pages", () => {
    const { container } = render(
      <MemoryRouter>
        <StationsPage />
      </MemoryRouter>,
    );

    expect(container.querySelector('a[href="/stations/AUS"]')).toBeTruthy();
    expect(container.querySelector('a[href="/stations/DAL"]')).toBeTruthy();
  });
});
