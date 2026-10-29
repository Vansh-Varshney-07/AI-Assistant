import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

/** Model output stays inert: no raw HTML, remote pixels, embeds or navigation.
 * URLs remain visible for inspection. The host keeps its navigation deny rules.
 * Parsing reuses remark; Wayfinder does not implement a Markdown parser.
 */
export function Markdown({text}:{text:string}){
  return <div className="markdown"><ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml
    components={{
      img:({alt})=><span className="image-reference">Image reference: {alt||'Unlabelled image'} (not loaded)</span>,
      a:({children,href})=><span className="source-link">{children}{href&&<span className="source-link-url"> ({href})</span>}</span>,
      table:({children})=><div className="table-scroll" tabIndex={0} role="region" aria-label="Response table"><table>{children}</table></div>,
      pre:({children})=><pre tabIndex={0} aria-label="Code block">{children}</pre>,
    }}>{text}</ReactMarkdown></div>;
}
