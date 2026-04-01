import {
  type UseSuspenseQueryOptions,
  useSuspenseQueries,
  useSuspenseQuery,
} from "@tanstack/react-query";
import { Suspense } from "react";
import bobPic from "@/assets/profiles/bobphoto.jpg";
import devPic from "@/assets/profiles/devphoto.jpg";
import dylanPic from "@/assets/profiles/dylanphoto.jpg";
import franklinPic from "@/assets/profiles/franklinphoto.jpg";
import { DockDemo } from "@/components/navigation";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchMemberCommits, fetchMemberIssues } from "@/lib/gitlabStats";

interface TeamMember {
  name: string;
  role: string;
  bio: string;
  profilePic: string;
  gitlabUsername: string;
  commitAuthor?: string;
  tests: number;
}

const TEAM_MEMBERS: TeamMember[] = [
  {
    name: "Dev Shroff",
    role: "Frontend Developer and API Integrator",
    bio: "Second-year CS major interested in data analysis and machine learning for financial applications. Likes interior design and cornflower blue.",
    profilePic: devPic,
    gitlabUsername: "devbshroff",
    tests: 5,
  },
  {
    name: "Bob Zhu",
    role: "Frontend Developer and UI/UX Designer",
    bio: "Second-year CS major interested in machine learning. Likes to run and seafoam green.",
    profilePic: bobPic,
    gitlabUsername: "zhubob3",
    tests: 6,
  },
  {
    name: "Franklin Wright",
    role: "Frontend Developer and Data Gatherer",
    bio: "Second-year CS major with a minor in history. Likes to learn and sapphire blue.",
    profilePic: franklinPic,
    gitlabUsername: "franklinwright",
    tests: 5,
  },
  {
    name: "Dylan Dang",
    role: "Backend Developer and Database Administrator",
    bio: "Second-year CS major focusing on backend infrastructure and data integrity.",
    profilePic: dylanPic,
    gitlabUsername: "dylan-dang",
    commitAuthor: "endercraft2319",
    tests: 6,
  },
];

const DATA_SOURCES = [
  {
    name: "Amtraker API",
    url: "https://amtraker.com/",
    description:
      "We pulled station names, codes, and locations using this REST API.",
  },
  {
    name: "National Transit Database",
    url: "https://www.transit.dot.gov/ntd/ntd-data",
    description: "We scraped ridership from transit agency reports.",
  },
  {
    name: "Census Bureau ACS API",
    url: "https://www.census.gov/data/developers/data-sets/acs-5year.html",
    description:
      "We queried demographic data like income and car access for each state.",
  },
];

const TOOLS = [
  { name: "React", use: "Frontend framework for building a responsive UI." },
  { name: "Postman", use: "Designing and testing our RESTful API." },
  { name: "AWS", use: "Hosting the production website with HTTPS support." },
  { name: "GitLab", use: "Version control and issue tracking." },
  {
    name: "Magic UI",
    use: "UI component library for advanced interactive components.",
  },
];

function commitsQueryOpt(member: TeamMember) {
  return {
    queryKey: ["about", "stats", "member", member.gitlabUsername, "commits"],
    queryFn: () =>
      fetchMemberCommits(member.commitAuthor ?? member.gitlabUsername),
  };
}

function issuesQueryOpt(member: TeamMember) {
  return {
    queryKey: ["about", "stats", "member", member.gitlabUsername, "issues"],
    queryFn: () => fetchMemberIssues(member.gitlabUsername),
  };
}

function testsQueryOpts(member: TeamMember) {
  return {
    queryKey: ["about", "stats", "member", member.gitlabUsername, "tests"],
    queryFn: () => member.tests,
  };
}

function TotalStatSuspense({
  ...props
}: {
  queries: UseSuspenseQueryOptions<number>[];
  children: string;
}) {
  return (
    <Suspense
      fallback={
        <div className="text-center">
          <Skeleton className="mx-auto h-9 w-12" />
          <Skeleton className="mx-auto mt-2 h-4 w-24" />
        </div>
      }
    >
      <TotalStat {...props} />
    </Suspense>
  );
}

function TotalStat({
  queries,
  children,
}: {
  queries: UseSuspenseQueryOptions<number>[];
  children: string;
}) {
  const results = useSuspenseQueries({ queries });

  return (
    <div className="text-center">
      <p className="font-bold text-3xl">
        {results.reduce((acc, r) => acc + (r.data ?? 0), 0)}
      </p>
      <p className="text-neutral-500 text-sm uppercase tracking-widest">
        {children}
      </p>
    </div>
  );
}

function TotalStats() {
  return (
    <div className="mb-12 grid grid-cols-3 gap-4 border-neutral-200 border-y py-6 dark:border-neutral-800">
      <TotalStatSuspense queries={TEAM_MEMBERS.map(commitsQueryOpt)}>
        Total Commits
      </TotalStatSuspense>
      <TotalStatSuspense queries={TEAM_MEMBERS.map(issuesQueryOpt)}>
        Total Issues
      </TotalStatSuspense>
      <TotalStatSuspense queries={TEAM_MEMBERS.map(testsQueryOpts)}>
        Unit Tests
      </TotalStatSuspense>
    </div>
  );
}

function TeamMemberStatSuspense({
  ...props
}: {
  options: UseSuspenseQueryOptions<number>;
  children: string;
}) {
  return (
    <Suspense
      fallback={
        <div className="flex flex-col items-center gap-1">
          <Skeleton className="h-5 w-8" />
          <Skeleton className="h-3 w-14" />
        </div>
      }
    >
      <TeamMemberStat {...props} />
    </Suspense>
  );
}

function TeamMemberStat({
  options,
  children,
}: {
  options: UseSuspenseQueryOptions<number>;
  children: string;
}) {
  const { data } = useSuspenseQuery(options);
  return (
    <div>
      <p className="font-bold">{data}</p>
      <p className="text-[10px] text-neutral-400 uppercase">{children}</p>
    </div>
  );
}

function TeamMemberStats({ member }: { member: TeamMember }) {
  return (
    <div className="mt-6 flex justify-between border-neutral-100 border-t pt-4 text-center dark:border-neutral-800">
      <TeamMemberStatSuspense options={commitsQueryOpt(member)}>
        Commits
      </TeamMemberStatSuspense>
      <TeamMemberStatSuspense options={issuesQueryOpt(member)}>
        Issues
      </TeamMemberStatSuspense>
      <TeamMemberStatSuspense options={testsQueryOpts(member)}>
        Tests
      </TeamMemberStatSuspense>
    </div>
  );
}

function TeamMemberCard({ member }: { member: TeamMember }) {
  return (
    <div className="flex flex-col rounded-xl border border-neutral-200 bg-white p-6 shadow-sm dark:border-neutral-800 dark:bg-neutral-900">
      <div className="flex items-center gap-4">
        <div className="h-16 w-16 overflow-hidden rounded-full bg-neutral-200 dark:bg-neutral-700">
          {member.profilePic ? (
            <img
              src={member.profilePic}
              alt={member.name}
              className="h-full w-full object-cover"
            />
          ) : (
            <span className="flex h-full w-full items-center justify-center font-bold text-xl">
              {member.name.charAt(0)}
            </span>
          )}
        </div>
        <div>
          <h3 className="font-semibold text-lg">{member.name}</h3>
          <p className="text-neutral-500 text-sm dark:text-neutral-400">
            {member.role}
          </p>
        </div>
      </div>
      <p className="mt-4 grow text-neutral-600 text-sm dark:text-neutral-300">
        {member.bio}
      </p>
      <TeamMemberStats member={member} />
    </div>
  );
}

function AboutContent() {
  return (
    <div className="w-full max-w-5xl pt-10">
      <DescriptionSection />
      <TotalStats />

      <h2 className="mb-6 font-bold text-2xl">The Team</h2>
      <div className="mb-16 grid grid-cols-1 gap-6 md:grid-cols-2">
        {TEAM_MEMBERS.map((member) => (
          <TeamMemberCard key={member.name} member={member} />
        ))}
      </div>
      <div className="mb-16 grid grid-cols-1 gap-12 md:grid-cols-2">
        <DataSourcesSection />
        <ToolsSection />
      </div>
      <ProjectLinksSection />
    </div>
  );
}

function DescriptionSection() {
  return (
    <section className="mb-16 text-center">
      <h1 className="mb-4 font-bold text-5xl tracking-tight">RailReach</h1>
      <p className="mx-auto max-w-3xl text-lg text-neutral-600 leading-relaxed dark:text-neutral-400">
        RailReach aims to improve awareness of rail transport for underserved
        communities across America. By connecting{" "}
        <strong>Amtrak Stations</strong>, <strong>Major Routes</strong>, and{" "}
        <strong>States</strong>, we empower users to see how public transit
        intersects with poverty levels, income, and vehicle access. Join us in
        "voting with your ridership" to influence the future of national
        infrastructure funding.
      </p>
    </section>
  );
}

function ProjectLinksSection() {
  return (
    <section className="rounded-2xl bg-neutral-100 p-8 text-center dark:bg-neutral-900">
      <h2 className="mb-4 font-bold text-xl">Project Links</h2>
      <div className="flex justify-center gap-8">
        <a
          href="https://gitlab.com/rail-reach/cs373-group-53380-01"
          className="font-medium hover:text-blue-500"
        >
          GitLab Repository
        </a>
        <a
          href="https://documenter.getpostman.com/view/52516897/2sBXcDHh5J"
          className="font-medium hover:text-blue-500"
        >
          Postman Documentation
        </a>
      </div>
    </section>
  );
}

function ToolsSection() {
  return (
    <section>
      <h2 className="mb-6 font-bold text-2xl">Tools Used</h2>
      <div className="grid grid-cols-1 gap-2">
        {TOOLS.map((tool) => (
          <div key={tool.name} className="text-sm">
            <span className="font-bold">{tool.name}:</span>{" "}
            <span className="text-neutral-600 dark:text-neutral-400">
              {tool.use}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

function DataSourcesSection() {
  return (
    <section>
      <h2 className="mb-6 font-bold text-2xl">Data Sources</h2>
      <div className="space-y-4">
        {DATA_SOURCES.map((source) => (
          <div key={source.name}>
            <a
              href={source.url}
              target="_blank"
              className="font-semibold text-blue-600 hover:underline"
            >
              {source.name}
            </a>
            <p className="text-neutral-600 text-sm dark:text-neutral-400">
              {source.description}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

export function AboutPage() {
  return (
    <div className="relative flex min-h-screen flex-col items-center overflow-x-hidden bg-neutral-50 px-4 pb-24 dark:bg-neutral-950">
      <AboutContent />
      <DockDemo />
    </div>
  );
}
