import React from 'react';

export default function A4Preview({ paper, sheets, logoDataUri }) {
  if (!paper || !sheets || sheets.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-slate-400 bg-white rounded-xl border border-dashed border-slate-300">
        <p className="font-medium text-sm">Paste questions or choose a sample to render the locked A4 preview.</p>
      </div>
    );
  }

  const is3b = paper.template === '3b';
  const logoUrl = logoDataUri || '/assets/logo.jpg';

  return (
    <div className="flex flex-col items-center gap-8 py-4 overflow-y-auto max-h-[calc(100vh-140px)] select-none">
      {sheets.map((sheet, sheetIdx) => {
        const pageNum = sheet.page_num;
        const totalPages = sheet.total_pages;

        return (
          <div key={sheetIdx} className="relative group">
            {/* Sheet Badge */}
            <div className="absolute -top-3 left-4 bg-slate-800 text-white text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded shadow">
              Sheet {pageNum} of {totalPages} ({is3b ? 'Template 3b MCQ' : 'Template 3a Theory'})
            </div>

            {/* A4 Sheet (Locked 794px width x 1123px height = 297mm @ 96dpi) */}
            <section className="a4-sheet">
              {/* Outer Margin Footer on Every Sheet */}
              <div className="a4-footer">
                {paper.header.school} · {paper.header.class_name} · {paper.header.subject} · {paper.header.paper_name} · Page {pageNum} of {totalPages}
              </div>

              {/* Inset Border (4px double #1a1a1a) */}
              <div className="a4-inner-border">
                {/* Background Watermark (7% opacity grayscale) */}
                <img
                  src={logoUrl}
                  alt="Watermark"
                  className="a4-watermark"
                />

                {/* Content Container (z-index 1 above watermark) */}
                <div className="a4-content">
                  {/* Masthead Header (Sheet 1 only) */}
                  {sheet.has_header && (
                    <>
                      <div className="flex items-center gap-3 pb-3 mb-3 border-b-[2.5px] border-[#1a1a1a]">
                        {/* School Logo */}
                        <img
                          src={logoUrl}
                          alt="Logo"
                          style={{ width: is3b ? '86px' : '94px', height: 'auto' }}
                          className="flex-shrink-0"
                        />

                        {/* Center Info Block */}
                        <div className="flex-1 text-center">
                          <h1
                            style={{ fontSize: is3b ? '28px' : '30px' }}
                            className="font-bold leading-tight tracking-tight text-[#111]"
                          >
                            {paper.header.school}
                          </h1>
                          <p style={{ fontSize: is3b ? '13px' : '13.5px' }} className="text-[#333]">
                            {paper.header.address}
                          </p>
                          <div
                            style={{ fontSize: is3b ? '13px' : '13.5px' }}
                            className="font-bold tracking-widest mt-0.5 uppercase text-[#111]"
                          >
                            {paper.header.paper_name} {paper.header.month_year ? `— ${paper.header.month_year}` : ''}
                          </div>
                        </div>

                        {/* Roll No. Boxes */}
                        <div className="flex-shrink-0 text-center">
                          <div className="text-[11px] font-semibold mb-1">Roll No.</div>
                          <div className="flex gap-[3px]">
                            {Array.from({ length: paper.header.roll_no_boxes || 4 }).map((_, i) => (
                              <span
                                key={i}
                                className="inline-block w-[22px] h-[26px] border border-[#1a1a1a]"
                              />
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Header Details Table */}
                      {!is3b ? (
                        /* 3a Theory Details Table */
                        <table className="w-full border-collapse border border-[#1a1a1a] text-[13px] mb-3">
                          <tbody>
                            <tr>
                              <td className="border border-[#1a1a1a] px-2.5 py-1">
                                Class: <span className="font-bold">{paper.header.class_name}</span>
                              </td>
                              <td className="border border-[#1a1a1a] px-2.5 py-1">
                                Subject: <span className="font-bold">{paper.header.subject}</span>
                              </td>
                              <td className="border border-[#1a1a1a] px-2.5 py-1">
                                Date: <span className="font-bold">{paper.header.date || '—'}</span>
                              </td>
                            </tr>
                            <tr>
                              <td className="border border-[#1a1a1a] px-2.5 py-1">
                                Marks: <span className="font-bold">{paper.header.marks}</span>
                              </td>
                              <td className="border border-[#1a1a1a] px-2.5 py-1">
                                Exam: <span className="font-bold">{paper.header.paper_name}</span>
                              </td>
                              <td className="border border-[#1a1a1a] px-2.5 py-1">
                                Time: <span className="font-bold">{paper.header.time}</span>
                              </td>
                            </tr>
                            <tr>
                              <td colSpan={3} className="border border-[#1a1a1a] px-2.5 py-1">
                                Name of the Student : <span className="border-b border-dotted border-[#1a1a1a] inline-block w-[70%]" />
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      ) : (
                        /* 3b MCQ Details Table (4 columns) */
                        <table className="w-full border-collapse border border-[#1a1a1a] text-[12px] mb-2.5">
                          <tbody>
                            <tr>
                              <td className="border border-[#1a1a1a] px-2 py-0.5">
                                Class: <span className="font-bold">{paper.header.class_name}</span>
                              </td>
                              <td className="border border-[#1a1a1a] px-2 py-0.5">
                                Subject: <span className="font-bold">{paper.header.subject}</span>
                              </td>
                              <td className="border border-[#1a1a1a] px-2 py-0.5">
                                Exam: <span className="font-bold">{paper.header.paper_name}</span>
                              </td>
                              <td className="border border-[#1a1a1a] px-2 py-0.5">
                                Date: <span className="font-bold">{paper.header.date || '—'}</span>
                              </td>
                            </tr>
                            <tr>
                              <td className="border border-[#1a1a1a] px-2 py-0.5">
                                Questions: <span className="font-bold">{paper.groups.reduce((acc, g) => acc + g.questions.length, 0)}</span>
                              </td>
                              <td className="border border-[#1a1a1a] px-2 py-0.5">
                                Max. Marks: <span className="font-bold">{paper.header.marks}</span>
                              </td>
                              <td colSpan={2} className="border border-[#1a1a1a] px-2 py-0.5">
                                Time: <span className="font-bold">{paper.header.time}</span>
                              </td>
                            </tr>
                            <tr>
                              <td colSpan={3} className="border border-[#1a1a1a] px-2 py-0.5">
                                Name of the Student : <span className="border-b border-dotted border-[#1a1a1a] inline-block w-[65%]" />
                              </td>
                              <td className="border border-[#1a1a1a] px-2 py-0.5">
                                Roll No.:
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      )}
                    </>
                  )}

                  {/* Template 3a Content Body */}
                  {!is3b && (
                    <div className="space-y-3">
                      {sheet.groups.map((group, gIdx) => (
                        <div key={gIdx} className="mb-3">
                          {/* Group Heading (17.5px bold) */}
                          <div className="font-bold text-[17.5px] mb-1.5 flex justify-between items-baseline">
                            <span>
                              {group.group_id}) {group.heading}
                            </span>
                            {group.marks_display && (
                              <span className="font-semibold text-[16px] pl-3 whitespace-nowrap">
                                {group.marks_display}
                              </span>
                            )}
                          </div>

                          {/* Questions */}
                          <div className="space-y-1.5 text-[16px] leading-[1.75]">
                            {group.questions.map((q, qIdx) => {
                              if (q.diagram && q.diagram.placement === 'side') {
                                return (
                                  <div key={qIdx} className="flex gap-4 items-start my-2">
                                    {/* Hatched Figure Box */}
                                    <div
                                      style={{ width: `${q.diagram.width_px || 280}px`, height: `${q.diagram.height_px || 160}px` }}
                                      className="diagram-hatch flex items-center justify-center p-2 text-center flex-shrink-0"
                                    >
                                      <pre className="font-mono text-[10px] text-[#555] whitespace-pre-wrap leading-tight">
                                        {q.diagram.caption}
                                      </pre>
                                    </div>
                                    <div className="flex-1">
                                      <div>{q.q_num}. {q.text}</div>
                                    </div>
                                  </div>
                                );
                              }

                              if (q.diagram && q.diagram.placement === 'below') {
                                return (
                                  <div key={qIdx} className="my-2">
                                    <div>{q.q_num}. {q.text}</div>
                                    {/* Large Hatched Map Box */}
                                    <div
                                      style={{ width: '100%', height: '520px' }}
                                      className="diagram-hatch flex items-center justify-center p-4 text-center my-2"
                                    >
                                      <pre className="font-mono text-[12px] text-[#555] font-semibold whitespace-pre-wrap">
                                        {q.diagram.caption}
                                      </pre>
                                    </div>
                                  </div>
                                );
                              }

                              return (
                                <div key={qIdx} className="flex gap-2">
                                  <span className="font-medium flex-shrink-0">{q.q_num}.</span>
                                  <span className="flex-1">{q.text}</span>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      ))}

                      {/* Continuation Note */}
                      {sheet.continuation_note && (
                        <div className="text-right italic text-[11px] text-[#555] mt-4 font-serif">
                          {sheet.continuation_note}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Template 3b Content Body */}
                  {is3b && (
                    <div>
                      {/* Important Instructions Box */}
                      {sheet.has_instructions && (
                        <div className="border border-[#1a1a1a] p-2 text-[11.5px] leading-snug mb-3">
                          <div className="font-bold tracking-wider text-[11.5px] uppercase mb-0.5">
                            IMPORTANT INSTRUCTIONS
                          </div>
                          <ol className="list-decimal pl-4 space-y-0.5 text-[11px]">
                            <li>
                              This paper contains {paper.groups.reduce((acc, g) => acc + g.questions.length, 0)} questions (in {paper.groups.length} sections), all compulsory.
                            </li>
                            <li>
                              Each question carries 1 mark, only ONE of (1)–(4) is correct.
                            </li>
                            <li>
                              Darken the OMR circle with blue/black ball pen; rough work in the space provided.
                            </li>
                          </ol>
                        </div>
                      )}

                      {/* 2-Column Body Layout (Locked 14px text, line-height 1.5) */}
                      <div className="grid grid-cols-2 gap-x-5 text-[14px] leading-[1.45]">
                        {/* We distribute questions between Left Col and Right Col */}
                        {(() => {
                          const allQs = [];
                          sheet.groups.forEach(g => {
                            allQs.push({ isSection: true, title: g.section_name || g.heading });
                            g.questions.forEach(q => allQs.push({ isSection: false, q }));
                          });

                          const mid = Math.ceil(allQs.length / 2);
                          const leftCol = allQs.slice(0, mid);
                          const rightCol = allQs.slice(mid);

                          const renderColItem = (item, idx) => {
                            if (item.isSection) {
                              return (
                                <div
                                  key={idx}
                                  className="text-center font-bold text-[12px] uppercase tracking-wider border-y border-[#1a1a1a] py-0.5 my-2"
                                >
                                  {item.title}
                                </div>
                              );
                            }
                            const q = item.q;
                            return (
                              <div key={idx} className="mb-2">
                                <div className="font-normal">
                                  {q.q_num}. {q.text}
                                </div>
                                {q.options && q.options.length === 4 && (
                                  <div className="grid grid-cols-2 gap-x-3 text-[12.5px] mt-0.5 pl-2 text-[#222]">
                                    <div>(1) {q.options[0]}</div>
                                    <div>(2) {q.options[1]}</div>
                                    <div>(3) {q.options[2]}</div>
                                    <div>(4) {q.options[3]}</div>
                                  </div>
                                )}
                              </div>
                            );
                          };

                          return (
                            <>
                              <div className="border-r border-[#bbb] pr-3">
                                {leftCol.map(renderColItem)}
                              </div>
                              <div className="pl-1">
                                {rightCol.map(renderColItem)}
                              </div>
                            </>
                          );
                        })()}
                      </div>

                      {/* Rough Work Box (Last Sheet only) */}
                      {sheet.has_rough_work && (
                        <div className="border border-[#1a1a1a] h-[75px] mt-3 p-1.5 text-[11px] italic text-[#555]">
                          Space for rough work
                        </div>
                      )}

                      {/* Continuation Note */}
                      {sheet.continuation_note && (
                        <div className="text-right italic text-[11px] text-[#555] mt-2 font-serif">
                          {sheet.continuation_note}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </section>
          </div>
        );
      })}
    </div>
  );
}
