import { cn } from "./utils";

describe("cn", () => {
  it("merges conditional class names", () => {
    expect(cn("p-2", false && "hidden", "text-sm")).toBe("p-2 text-sm");
  });

  it("resolves conflicting tailwind utilities", () => {
    expect(cn("p-2", "p-4", "text-white", "text-black")).toBe("p-4 text-black");
  });
});
