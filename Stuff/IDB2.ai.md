Summary of AI Interactions: We utilized GPT 5.3 to debug a variety of issues and to get an idea of how the different tests (unit, acceptance, etc.) should function. It also helped us figure out API wiring and some deployment issues when the live site wasn’t behaving correctly. AI was mainly used for narrowing down where a problem was coming from so we could test it.


Reflection on Use: We got a better understanding of how Bun Lockfile works, how React Query connects to Flask, and why our CI pipeline failed for non-obvious reasons. It also helped us move faster with updating our tests after the backend architecture changed throughout the project. Obviously, we didn’t blindly accept every suggestion by AI. Oftentimes it gave a too complicated idea, or the solution it gave didn’t match the style of the site, so we ignored the AI’s output. Usually we judged AI’s output by integrating its fixes and running the code immediately, checking type errors, checking tests, and checking the project requirements. This mattered a lot because some suggestions looked fine at first but were actually wrong when we tested them in our own repo.
Evidence of Independent Work: 
Pagination in frontend/pages/StationsPage.tsx
Before AI:
function StationsContent() {
  const {
    data: {
      data: stations = [],
      pagination: { totalItems },
    },
  } = useStationsQuery();


  return (
    <>
      <p className="mb-8 text-muted-foreground">
        Showing {stations.length} of {totalItems} instances
      </p>
      <BentoGrid className="lg:grid-rows-1">
After AI:
const DEFAULT_PAGE_SIZE = 24;


function parsePositiveInt(value: string | null, fallback: number): number {
  const parsed = Number.parseInt(value ?? "", 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}


function StationsContent({
  page,
  pageSize,
  onPageChange,
  onPageSizeChange,
}: {
  page: number;
  pageSize: number;
  onPageChange: (nextPage: number) => void;
  onPageSizeChange: (nextPageSize: number) => void;
}) {
  const {
    data: { data: stations = [], pagination },
  } = useStationsQuery({ page, pageSize });
Explanation: AI helped us think through how to do pagination in the pages. We still had to decide the page size, update the query usage, use the correct URL parameters, and test navigation/counts.


React Router fix in frontend/components/ui/bento-grid.tsx
Before AI:
<Button variant="link" asChild size="sm" className="pointer-events-auto p-0">
  <a href={href}>
    {cta}
    <ArrowRightIcon className="ms-2 h-4 w-4 rtl:rotate-180" />
  </a>
</Button>
After AI:
<Button variant="link" asChild size="sm" className="pointer-events-auto p-0">
  <Link to={href}>
    {cta}
    <ArrowRightIcon className="ms-2 h-4 w-4 rtl:rotate-180" />
  </Link>
</Button>
Explanation: AI helped point out that we were still incorrectly using a plain anchor tag inside the React Router app, meaning that every click refreshed the whole page. We changed them to React Router Link components (in both card layouts), and then we tested navigation to make sure pages could switch between each other without fully reloading or causing any other issues.
“I confirm that the AI was used only as a helper (explainer, debugger, reviewer) and not as a code generator. All code submitted is my own work.”