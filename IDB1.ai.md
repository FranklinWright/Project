Summary of AI Interactions: We utilized Gemini 3 to start off the project and develop our website's visual features. We collaborated with the AI to learn how to use Bun to download all project packages and resolve installation errors. Additionally, we used it to understand the setup of Magic UI components, such as the navigation dock and grid layouts. We also used Gemini to determine how to support images on our site with declarations, which led us to Stack Overflow. This approach helped us verify that all website elements functioned properly from the start.

Reflection on Use: We gained a better understanding of how Bun manages our project files and how to maintain a clean environment. By correcting setup errors, we learned to manage our downloads and run the site on our machines. During UI development, we used Magic UI to build a professional, interactive site. We chose what to keep from AI by ensuring everything aligned with our project style. We dismissed suggestions that were too complex or did not match RailReach's simple design. We identified poor suggestions by immediately testing the code to prevent breaking our project setup.

Evidence of Independent Work: 

In ui/bento-grid.tsx:

Before AI:

description: string

href: string

cta: string

After AI:

description: string | ReactNode

href?: string

cta?: string

Explanation: AI helped us notice that some cards don’t always have a link/CTA (“call to action”) yet, but the original component (from Magic UI) required href and cta, which caused type errors. So we changed those props to be optional and allowed description to be a ReactNode so that we can actually render the cards for phase 1 and keep the same UI without the full data that the UI component requires.

In ui/bento-grid.tsx:

Before AI:

\<Button variant="link" asChild size="sm" className="pointer-events-auto p-0"\>

  \<a href={href}\>{cta}\<ArrowRightIcon className="ms-2 h-4 w-4 rtl:rotate-180" /\>\</a\>

\</Button\>

After AI:

{href && (

  \<Button variant="link" asChild size="sm" className="pointer-events-auto p-0"\>

    \<a href={href}\>{cta}\<ArrowRightIcon className="ms-2 h-4 w-4 rtl:rotate-180" /\>\</a\>

  \</Button\>

)}

Explanation: AI suggested guarding the CTA rendering because some bento cards don’t have an href yet, so we added a conditional render.

“I confirm that the AI was used only as a helper (explainer, debugger, reviewer) and not as a code generator. All code submitted is my own work.”