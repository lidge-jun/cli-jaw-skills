import React from "react";
import { TitleSlide, ContentSlide, CodeSlide, DiagramSlide, Caption } from "../components";
import type { TimelineElement } from "./schema";
import type { Theme } from "../theme";

type Props = {
  element: TimelineElement;
  theme: Theme;
};

export const ElementRouter: React.FC<Props> = ({ element, theme }) => {
  const p = element.props as Record<string, unknown>;

  switch (element.type) {
    case "title":
      return (
        <TitleSlide
          title={String(p.title || "")}
          subtitle={p.subtitle ? String(p.subtitle) : undefined}
          designTheme={theme}
        />
      );
    case "content":
      return (
        <ContentSlide
          header={String(p.header || "")}
          content={p.content ? String(p.content) : undefined}
          bulletPoints={Array.isArray(p.bulletPoints) ? p.bulletPoints.map(String) : undefined}
          designTheme={theme}
        />
      );
    case "code":
      return (
        <CodeSlide
          code={String(p.code || "")}
          language={p.language ? String(p.language) : undefined}
          title={p.title ? String(p.title) : undefined}
          designTheme={theme}
        />
      );
    case "diagram":
    case "image":
      return (
        <DiagramSlide
          src={p.src ? String(p.src) : undefined}
          title={p.title ? String(p.title) : undefined}
          caption={p.caption ? String(p.caption) : undefined}
          fit={(p.fit as "cover" | "contain" | "fill") || "contain"}
          designTheme={theme}
        />
      );
    default:
      return (
        <TitleSlide title={`Unknown type: ${element.type}`} designTheme={theme} />
      );
  }
};
