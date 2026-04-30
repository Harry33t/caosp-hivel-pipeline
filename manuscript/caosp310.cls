%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PROBLEMY - DORIESIT
% - pouzivanie \it, \bf, \rm v .cls -> nahradit \itshape{}, etc.
% - input    \input{size1\@ptsize.clo}
% - insertplot - prerobit na graphicx
% - vyhodit normalsize podla A&A?
%
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% csosp.cls version 3.10 as of 20171025-20241129
%
% This is CAOSP.CLS version 3.10, the LaTeX2e DocumentClass file
% from the Astronomical Institute, Slovak Academy of Sciences for the
% journal Contributions of the Astronomical Observatory Skalnate Pleso
%
% It is for use with LaTeX2e
%
% Credits: Richard Komzik, Ondrej Nentvich, Julius Koza
%
% Please report all errors to:  Richard KOMZIK
%                               Astronomical Institue
%                               Slovak Academy of Sciences
%                               SK 059 60 Tatranska Lomnica
%                               The SLOVAK REPUBLIC
%
%           E-mail (INTERNET):  rkomzik@ta3.sk
%
%%
%%
%% \CharacterTable
%%  {Upper-case    \A\B\C\D\E\F\G\H\I\J\K\L\M\N\O\P\Q\R\S\T\U\V\W\X\Y\Z
%%   Lower-case    \a\b\c\d\e\f\g\h\i\j\k\l\m\n\o\p\q\r\s\t\u\v\w\x\y\z
%%   Digits        \0\1\2\3\4\5\6\7\8\9
%%   Exclamation   \!     Double quote  \"     Hash (number) \#
%%   Dollar        \$     Percent       \%     Ampersand     \&
%%   Acute accent  \'     Left paren    \(     Right paren   \)
%%   Asterisk      \*     Plus          \+     Comma         \,
%%   Minus         \-     Point         \.     Solidus       \/
%%   Colon         \:     Semicolon     \;     Less than     \<
%%   Equals        \=     Greater than  \>     Question mark \?
%%   Commercial at \@     Left bracket  \[     Backslash     \\
%%   Right bracket \]     Circumflex    \^     Underscore    \_
%%   Grave accent  \`     Left brace    \{     Vertical bar  \|
%%   Right brace   \}     Tilde         \~}

\typeout{} \typeout{} \typeout{}
\typeout{  Document Class    C A O S P}
\typeout{}
\typeout{    for the "Contributions of the Astonomical Observatory Skalnate Pleso" journal}
\typeout{               ISSN (on-line version):  1336-0337}
\typeout{               ISSN (printed version):  1335-1842}
\typeout{               CODEN:                   CAOPF8}
\typeout{}
\typeout{}
\typeout{ Version 3.10 <2024-11-29>}\typeout{} \typeout{}

\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{caosp}[2024/11/29 v3.10
^^JLaTeX document class for 
^^JContributions of the Astronomical Observatory Skalnate Pleso journal^^J]

\DeclareOldFontCommand{\rm}{\normalfont\rmfamily}{\mathrm}
\DeclareOldFontCommand{\sf}{\normalfont\sffamily}{\mathsf}
\DeclareOldFontCommand{\tt}{\normalfont\ttfamily}{\mathtt}
\DeclareOldFontCommand{\bf}{\normalfont\bfseries}{\mathbf}
\DeclareOldFontCommand{\it}{\normalfont\itshape}{\mathit}
\DeclareOldFontCommand{\sl}{\normalfont\slshape}{\@nomath\sl}
\DeclareOldFontCommand{\sc}{\normalfont\scshape}{\@nomath\sc}

\def\ch@ckobl#1#2{\@ifundefined{@#1}
 {\typeout{CAOSP warning: Missing
\expandafter\string\csname#1\endcsname}%
  \csname #1\endcsname{#2}}
 {}}

\newcommand\@ptsize{}
\newif\if@restonecol
\newif\if@titlepage
\@titlepagefalse
\DeclareOption{a4paper}
   {\setlength\paperheight {297mm}% 
    \setlength\paperwidth  {210mm}}
\DeclareOption{letterpaper}
   {\setlength\paperheight {11in}%
    \setlength\paperwidth  {8.5in}}
\DeclareOption{legalpaper}
   {\setlength\paperheight {14in}%
    \setlength\paperwidth  {8.5in}}
\DeclareOption{10pt}{\renewcommand\@ptsize{0}}
\DeclareOption{11pt}{\renewcommand\@ptsize{1}}
\DeclareOption{12pt}{\renewcommand\@ptsize{2}}
\DeclareOption{twoside}{\@twosidetrue  \@mparswitchtrue}
\DeclareOption{draft}{\setlength\overfullrule{5pt}}
\DeclareOption{final}{\setlength\overfullrule{0pt}}
\DeclareOption{twocolumn}{\@twocolumntrue}
\DeclareOption{openbib}{%
  \AtEndOfPackage{%
   \renewcommand\@openbib@code{%
      \advance\leftmargin\bibindent
      \itemindent -\bibindent
      \listparindent \itemindent
      \parsep \z@
      }%
   \renewcommand\newblock{\par}}%
}
\newif\ifaa@bibnumber
\DeclareOption{bibnumber}{\aa@bibnumbertrue%
  \def\aa@biblio{%
    \RequirePackage[sort&compress]{natbib}
    \bibpunct{[}{]}{,}{n}{}{,}%
    \def\@biblabel##1{##1.}%
    \bibliographystyle{plainnat}%
    \def\bibfont{\aa@bibliographyfont}%
    \setlength{\bibsep}{\z@}%
  }
}
\DeclareOption{bibauthoryear}{%
  \def\aa@biblio{%
    \RequirePackage{natbib}
    \bibpunct{(}{)}{;}{a}{}{,}%
    \def\bibfont{\aa@bibliographyfont}%
    \setlength{\bibsep}{\z@}%
  }%
}
\DeclareOption{bibyear}{%
  \def\aa@biblio{%
    \def\@biblabel##1{}%
    \def\@cite##1##2{{##1\if@tempswa , ##2\fi}}%
  }
}
%%% OPTIONS
\let\if@runhead\iffalse
\DeclareOption{runningheads}{\let\if@runhead\iftrue}
\let\if@envcntreset\iffalse
\DeclareOption{envcountreset}{\let\if@envcntreset\iftrue}
\let\if@envcntsect\iffalse
\DeclareOption{envcountsect}{\let\if@envcntsect\iftrue}
\let\if@referee\iffalse
\DeclareOption{referee}{\let\if@referee\iftrue}
\let\if@errata\iffalse
\DeclareOption{errata}{\let\if@errata\iftrue}
\let\if@supplement\iffalse
\DeclareOption{supplement}{\let\if@supplement\iftrue}
\let\if@nyobjects\iffalse
\DeclareOption{utf8}{%
  \def\aa@inputenc{\RequirePackage[utf8]{inputenc}}%
}
%
\ExecuteOptions{a4paper,twoside,twocolumn,utf8,fleqn,final,10pt,runningheads,bibauthoryear}
\ProcessOptions


%
\if\@ptsize 0
%
   \renewcommand\normalsize{%
      \@setfontsize\normalsize\@xpt{12}%
      \abovedisplayskip 8.55\p@ \@plus4\p@ \@minus5\p@
      \abovedisplayshortskip \z@ \@plus3\p@
      \belowdisplayshortskip 6\p@ \@plus3\p@ \@minus3\p@
      \belowdisplayskip \abovedisplayskip
      \let\@listi\@listI}
   \normalsize
   \newcommand\small{%
      \@setfontsize\small\@ixpt{11}%
      \abovedisplayskip 8.5\p@ \@plus3\p@ \@minus4\p@
      \abovedisplayshortskip \z@ \@plus2\p@
      \belowdisplayshortskip 4\p@ \@plus2\p@ \@minus2\p@
      \def\@listi{\leftmargin\leftmargini
                  \parsep 0\p@ \@plus1\p@ \@minus\p@
                  \topsep 8\p@ \@plus2\p@ \@minus4\p@
                  \itemsep0\p@}%
      \belowdisplayskip \abovedisplayskip
   }
   \newcommand\scriptsize{\@setfontsize\scriptsize\@viipt\@viiipt}
   \newcommand\tiny{\@setfontsize\tiny\@vipt\@viipt} 
   \newcommand\large{\@setfontsize\large\@xipt{13}}
   \newcommand\Large{\@setfontsize\Large\@xivpt{16}}
   \newcommand\LARGE{\@setfontsize\LARGE\@xviipt{20}}
   \newcommand\huge{\@setfontsize\huge\@xxpt{24}}
   \newcommand\Huge{\@setfontsize\Huge\@xxvpt{30}}
   %
   \setlength\parindent{15\p@}
   \setlength\smallskipamount{3\p@ \@plus 1\p@ \@minus 1\p@}
   \setlength\medskipamount{6\p@ \@plus 2\p@ \@minus 2\p@}
   \setlength\bigskipamount{12\p@ \@plus 4\p@ \@minus 4\p@}
   \setlength\headheight{12\p@}
   \setlength\headsep   {12\p@} % 
   \setlength\topskip   {10\p@}
   \setlength\footskip{30\p@}
   \setlength\maxdepth{.5\topskip}
   %
   \@settopoint\textwidth
   \setlength\marginparsep {10\p@}
   \setlength\marginparpush{5\p@}
   \setlength\oddsidemargin   {-30\p@}
   \setlength\evensidemargin  {-30\p@}
   \setlength\marginparwidth  {48\p@}
   \setlength\topmargin{-10pt}
   \setlength\footnotesep{8\p@}
   \setlength{\skip\footins}{9\p@ \@plus 4\p@ \@minus 2\p@}
   \setlength\floatsep    {12\p@ \@plus 2\p@ \@minus 2\p@}
   \setlength\textfloatsep{15\p@ \@plus 8\p@ \@minus 6\p@}
   \setlength\intextsep   {15\p@ \@plus 2\p@ \@minus 2\p@}
   \setlength\dblfloatsep    {12\p@ \@plus 2\p@ \@minus 2\p@}
   \setlength\dbltextfloatsep{15\p@ \@plus 8\p@ \@minus 6\p@}
   \setlength\@fptop{0\p@ }
   \setlength\@fpsep{12\p@ }
   \setlength\@fpbot{0\p@ \@plus 1fil}
   \setlength\@dblfptop{0\p@ }
   \setlength\@dblfpsep{12\p@ }
   \setlength\@dblfpbot{0\p@ \@plus 1fil}
   \setlength\partopsep{2\p@ \@plus 1\p@ \@minus 1\p@}
   \def\@listi{\leftmargin\leftmargini
               \parsep \z@
               \topsep 8\p@ \@plus2\p@ \@minus4\p@
               \itemsep\parsep}
   \let\@listI\@listi
   \@listi
   \def\@listii {\leftmargin\leftmarginii
                 \labelwidth\leftmarginii
                 \advance\labelwidth-\labelsep
                 \topsep    \z@
                 \parsep    \topsep
                 \itemsep   \parsep}
   \def\@listiii{\leftmargin\leftmarginiii
                 \labelwidth\leftmarginiii
                 \advance\labelwidth-\labelsep
                 \topsep    \z@
                 \parsep    \topsep
                 \itemsep   \parsep}
   \def\@listiv {\leftmargin\leftmarginiv
                 \labelwidth\leftmarginiv
                 \advance\labelwidth-\labelsep}
   \def\@listv  {\leftmargin\leftmarginv
                 \labelwidth\leftmarginv
                 \advance\labelwidth-\labelsep}
   \def\@listvi {\leftmargin\leftmarginvi
                 \labelwidth\leftmarginvi
                 \advance\labelwidth-\labelsep}
\else
   \input{size1\@ptsize.clo}
\fi

%%%--- Basic names
\def\abstractname{Abstract}%
\def\bibname{References}%
\def\chaptername{Chapter}%
\def\appendixname{Appendix}%
\def\contentsname{Contents}%
\def\listfigurename{List of figures}%
\def\listtablename{List of tables}%
\def\indexname{Index}%
\def\figurename{Figure}%
\def\tablename{Table}%
\def\acknowname{Acknowledgements}%
\def\keywordsname{Key words}%

\frenchspacing
\def~{\penalty\@M\kern3pt}

\widowpenalty=9000
\clubpenalty=9000

\lineskip 1pt \normallineskip 1pt
\def\baselinestretch{1}


%%%%%%%%%%%%%%%%%%%%%%% OPTIONS %%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%@twoside

\if@twoside 
 \oddsidemargin 52pt 
 \evensidemargin 54pt 
 \marginparwidth 107pt
\else 
 \oddsidemargin 54pt 
 \evensidemargin 54pt
 \marginparwidth 90pt
\fi

%%%%%%%%%%%%%%%%%%%%%%%@supplement

\if@supplement
\typeout{      SUPPLEMENT option used = pages with outer margin gray strip}
\typeout{} \typeout{}

 \if@referee
  \def\okrajtitullavyx{89}
  \def\okrajtitullavyy{-181}
  \def\okrajtitulpravyx{-362}
  \def\okrajtitulpravyy{-181}
  \def\okrajlavyx{77}
  \def\okrajlavyy{-142}
  \def\okrajpravyx{-373}
  \def\okrajpravyy{-142}
  \def\pasik
   {
    \multiput(0,-900)(1.9,0){24}{\rule{.15 pt}{26.5 cm}}
    \put(15,-180){{\huge \sf S}}
    \put(15,-205){{\huge \sf U}}
    \put(15,-230){{\huge \sf P}}
    \put(15,-255){{\huge \sf P}}
    \put(15,-280){{\huge \sf L}}
    \put(15,-305){{\huge \sf E}}
    \put(15,-330){{\huge \sf M}}
    \put(15,-355){{\huge \sf E}}
    \put(15,-380){{\huge \sf N}}
    \put(15,-405){{\huge \sf T}}
   }
 \else
  \def\okrajtitullavyx{89}
  \def\okrajtitullavyy{-144}
  \def\okrajtitulpravyx{-362}
  \def\okrajtitulpravyy{-144}
  \def\okrajlavyx{77}
  \def\okrajlavyy{-110}
  \def\okrajpravyx{-373}
  \def\okrajpravyy{-110}
  \def\pasik
   {
    \multiput(0,-830)(1.9,0){24}{\rule{.15 pt}{29.0 cm}}
    \put(15,-120){{\huge \sf S}}
    \put(15,-145){{\huge \sf U}}
    \put(15,-170){{\huge \sf P}}
    \put(15,-195){{\huge \sf P}}
    \put(15,-220){{\huge \sf L}}
    \put(15,-245){{\huge \sf E}}
    \put(15,-270){{\huge \sf M}}
    \put(15,-295){{\huge \sf E}}
    \put(15,-320){{\huge \sf N}}
    \put(15,-345){{\huge \sf T}}
   }
 \fi
\fi

%%%%%%%%%%%%%%%%%%%%%%%@referee

\if@referee
 \typeout{      REFEREE option used = double line skip}
 \typeout{} \typeout{}
 \def\normalsize{\@setsize\normalsize{18dd}\xpt\@xpt
  \abovedisplayskip 18pt plus2pt minus5pt
  \belowdisplayskip \abovedisplayskip
  \abovedisplayshortskip \z@ plus3pt
  \belowdisplayshortskip 8pt plus3pt minus3pt
 \def\@listi{\topsep 6pt plus 2pt minus 2pt
  \leftmargin \leftmargini
  \parsep 3pt plus 1pt minus 1pt
  \itemsep \parsep}}
 \def\small{\@setsize\small{16dd}\ixpt\@ixpt
  \abovedisplayskip 15pt plus 3pt minus 4pt
  \belowdisplayskip \abovedisplayskip
  \abovedisplayshortskip \z@ plus2pt
  \belowdisplayshortskip 6pt plus2pt minus 2pt
  \def\@listi{\topsep 6pt plus 2pt minus 2pt
   \leftmargin \leftmargini
   \parsep 3pt plus 1pt minus 1pt
  \itemsep \parsep}}
 \def\footnotesize{\@setsize\footnotesize{18dd}\xpt\@xpt
  \abovedisplayskip 18pt plus 2pt minus 5pt
  \belowdisplayskip \abovedisplayskip
  \abovedisplayshortskip \z@ plus 1pt
  \belowdisplayshortskip 8pt plus 1pt minus 2pt
 \def\@listi{\topsep 6pt plus 2pt minus 2pt
  \leftmargin \leftmargini
  \parsep 3pt plus 1pt minus 1pt
  \itemsep \parsep}}
 \def\scriptsize{\@setsize\scriptsize{14pt}\viiipt\@viiipt}
 \def\tiny{\@setsize\tiny{6pt}\vpt\@vpt}
 \def\large{\@setsize\large{24dd}\xivpt\@xivpt}
 \def\Large{\@setsize\Large{24dd}\xivpt\@xivpt}
 \def\LARGE{\@setsize\LARGE{30dd}\xviipt\@xviipt}
 \def\huge{\@setsize\huge{25pt}\xxpt\@xxpt}
 \def\Huge{\@setsize\Huge{30pt}\xxvpt\@xxvpt}

 \marginparsep 11pt
 \topskip 5pt
 \topmargin -63pt \headheight 12pt \headsep 15pt \footskip 10pt
 \textheight = 25.5cm
 \advance\textheight by \topskip
 \textwidth 345pt \columnsep 10pt \columnseprule 0pt

\else

 \def\normalsize{\@setsize\normalsize{12pt}\xpt\@xpt
  \abovedisplayskip 10pt plus2pt minus5pt
  \belowdisplayskip \abovedisplayskip
  \abovedisplayshortskip \z@ plus3pt
  \belowdisplayshortskip 6pt plus3pt minus3pt
  \let\@listi\@listI}
 \def\small{\@setsize\small{11pt}\ixpt\@ixpt
  \abovedisplayskip 8.5pt plus 3pt minus 4pt
  \belowdisplayskip \abovedisplayskip
  \abovedisplayshortskip \z@ plus2pt
  \belowdisplayshortskip 4pt plus2pt minus 2pt
  \def\@listi{\leftmargin\leftmargini 
   \topsep 4pt plus 2pt minus 2pt
   \parsep 2pt plus 1pt minus 1pt
  \itemsep \parsep}}
 \def\footnotesize{\@setsize\footnotesize{9.5pt}\viiipt\@viiipt
  \abovedisplayskip 6pt plus 2pt minus 4pt
  \belowdisplayskip \abovedisplayskip
  \abovedisplayshortskip \z@ plus 1pt
  \belowdisplayshortskip 3pt plus 1pt minus 2pt
  \def\@listi{\leftmargin\leftmargini \topsep 3pt plus 1pt minus 1pt
   \parsep 2pt plus 1pt minus 1pt
  \itemsep \parsep}}
 \def\scriptsize{\@setsize\scriptsize{8pt}\viipt\@viipt}
 \def\tiny{\@setsize\tiny{6pt}\vpt\@vpt}
 \def\large{\@setsize\large{14pt}\xiipt\@xiipt}
 \def\Large{\@setsize\Large{18pt}\xivpt\@xivpt}
 \def\LARGE{\@setsize\LARGE{22pt}\xviipt\@xviipt}
 \def\huge{\@setsize\huge{25pt}\xxpt\@xxpt}
 \def\Huge{\@setsize\Huge{30pt}\xxvpt\@xxvpt}

 \marginparsep 11pt
 \topmargin 27pt \headheight 12pt \headsep 25pt \footskip 30pt
 \textheight = 43\baselineskip
 \advance\textheight by \topskip
 \textwidth 345pt \columnsep 10pt \columnseprule 0pt

\fi

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


\normalsize




%\footnotesep 6.65pt
%\skip\footins 9pt plus 4pt minus 2pt
%\floatsep 20pt plus 2pt minus 2pt \textfloatsep 5pt plus 2pt minus 4pt
%\intextsep 5pt plus 2pt minus 2pt \@maxsep 12pt \dblfloatsep 5pt plus 2pt
%minus 2pt \dbltextfloatsep 12pt plus 2pt minus 4pt \@dblmaxsep 12pt
%\@fptop 0pt plus 1fil \@fpsep 8pt plus 2fil \@fpbot 0pt plus 1fil
%\@dblfptop 0pt plus 1fil \@dblfpsep 8pt plus 2fil \@dblfpbot 0pt plus 1fil
%\marginparpush 5pt
%\parskip 0pt plus 1pt \parindent 15pt \partopsep 2pt plus 1pt minus 1pt
%\@lowpenalty 51 \@medpenalty 151 \@highpenalty 301
%\@beginparpenalty -\@lowpenalty \@endparpenalty -\@lowpenalty \@itempenalty
%-\@lowpenalty

\def\part{\par \addvspace{4ex} \@afterindentfalse \secdef\@part\@spart}
\def\partname{Part} % <----------
\def\@part[#1]#2{
 \ifnum 
  \c@secnumdepth >\m@ne \refstepcounter{part}
  \addcontentsline{toc}{part}{\thepart \hspace{1em}#1}
 \else
  \addcontentsline{toc}{part}{#1}
 \fi 
 { \parindent 0pt \raggedright
  \ifnum 
   \c@secnumdepth >\m@ne \Large \bfseries \partname{}
   \thepart \par\nobreak 
  \fi 
  \huge
  \bfseries #2\markboth{}{}\par } 
  \nobreak \vskip 3ex \@afterheading }
\def\@spart#1{{\parindent 0pt \raggedright
 \huge \bfseries #1\par} \nobreak \vskip 3ex \@afterheading }
\def\section{\@startsection {section}{1}{\z@}{-3.5ex plus -1ex minus
 -.2ex}{2.3ex plus .2ex}{\large\bfseries}}
\def\subsection{\@startsection{subsection}{2}{\z@}{-3.25ex plus -1ex minus
 -.2ex}{1.5ex plus .2ex}{\normalsize\bfseries}}
\def\subsubsection{\@startsection{subsubsection}{3}{\z@}{-3.25ex plus
-1ex minus -.2ex}{1.5ex plus .2ex}{\normalsize\bfseries}}
\def\paragraph{\@startsection
 {paragraph}{4}{\z@}{3.25ex plus 1ex minus .2ex}{-1em}{\normalsize\bfseries}}
\def\subparagraph{\@startsection
 {subparagraph}{4}{\parindent}{3.25ex plus 1ex minus
 .2ex}{-1em}{\normalsize\bfseries}}


\setcounter{secnumdepth}{3}

\def\appendix{\par
 \setcounter{section}{0}
 \setcounter{subsection}{0}
 \def\thesection{\Alph{section}}
 \renewcommand{\theequation}{\thesection\arabic{equation}}
 \setcounter{equation}{0}
 \@addtoreset{equation}{section}
 \@startsection {section}{1}{\z@}{-3.5ex plus -1ex minus
 -.2ex}{2.3ex plus .2ex}{\large\bfseries}}

\leftmargini 25pt
\leftmarginii 22pt \leftmarginiii 18.7pt \leftmarginiv 17pt \leftmarginv 10pt
\leftmarginvi 10pt
\leftmargin\leftmargini
\labelsep 5pt
\labelwidth\leftmargini\advance\labelwidth-\labelsep
\def\@listI{\leftmargin\leftmargini \parsep 4pt plus 2pt minus 1pt\topsep 8pt
plus 2pt minus 4pt\itemsep 4pt plus 2pt minus 1pt}
\let\@listi\@listI
\@listi
\def\@listii{\leftmargin\leftmarginii
 \labelwidth\leftmarginii\advance\labelwidth-\labelsep
 \topsep 4pt plus 2pt minus 1pt
 \parsep 2pt plus 1pt minus 1pt
 \itemsep \parsep}
\def\@listiii{\leftmargin\leftmarginiii
 \labelwidth\leftmarginiii\advance\labelwidth-\labelsep
 \topsep 2pt plus 1pt minus 1pt
 \parsep \z@ \partopsep 1pt plus 0pt minus 1pt
 \itemsep \topsep}
\def\@listiv{\leftmargin\leftmarginiv
 \labelwidth\leftmarginiv\advance\labelwidth-\labelsep}
\def\@listv{\leftmargin\leftmarginv
 \labelwidth\leftmarginv\advance\labelwidth-\labelsep}
\def\@listvi{\leftmargin\leftmarginvi
 \labelwidth\leftmarginvi\advance\labelwidth-\labelsep}

\parskip 0pt plus 1pt
\topsep 10pt plus2pt minus5pt
\partopsep 0pt
\itemsep 0pt plus 1pt
\parindent 1.5em
\leftmargin    \parindent
\leftmargini   \leftmargin
\leftmarginii  \leftmargin
\leftmarginiii \leftmargin
\leftmarginiv  \leftmargin
\leftmarginv   \leftmargin
\leftmarginvi  \leftmargin
\labelwidth\leftmargini
\labelsep 4pt
\advance\labelwidth-\labelsep
\def\@listii{\leftmargin\leftmarginii
 \labelwidth\leftmarginii\advance\labelwidth-\labelsep
 \topsep \z@}
\def\@listiii{\leftmargin\leftmarginiii
 \labelwidth\leftmarginiii\advance\labelwidth-\labelsep
 \topsep \z@}
\def\@listiv{\leftmargin\leftmarginiv
 \labelwidth\leftmarginiv\advance\labelwidth-\labelsep}
\def\@listv{\leftmargin\leftmarginv
 \labelwidth\leftmarginv\advance\labelwidth-\labelsep}
\def\@listvi{\leftmargin\leftmarginvi
 \labelwidth\leftmarginvi\advance\labelwidth-\labelsep}


\def\vec#1{\ifmmode\mathchoice{\mbox{\boldmath$\displaystyle#1$}}
{\mbox{\boldmath$\textstyle#1$}}
{\mbox{\boldmath$\scriptstyle#1$}}
{\mbox{\boldmath$\scriptscriptstyle#1$}}\else
\hbox{\boldmath$\textstyle#1$}\fi}

\def\tens#1{\ifmmode\mathchoice{\mbox{$\sf\displaystyle#1$}}
{\mbox{$\sf\textstyle#1$}}
{\mbox{$\sf\scriptstyle#1$}}
{\mbox{$\sf\scriptscriptstyle#1$}}\else
\hbox{$\sf\textstyle#1$}\fi}


\def\@sect#1#2#3#4#5#6[#7]#8{\ifnum #2>\c@secnumdepth
     \def\@svsec{}\else
     \refstepcounter{#1}\edef\@svsec{\csname the#1\endcsname.\ }\fi
     \@tempskipa #5\relax
      \ifdim \@tempskipa>\z@
 \begingroup #6\relax
   \@hangfrom{\hskip #3\relax\@svsec}{\interlinepenalty \@M #8\par}
 \endgroup
       \csname #1mark\endcsname{#7}\addcontentsline
  {toc}{#1}{\ifnum #2>\c@secnumdepth \else
        \protect\numberline{\csname the#1\endcsname.}\fi
      #7}\else
 \def\@svsechd{#6\hskip #3\@svsec #8\csname #1mark\endcsname
        {#7}\addcontentsline
      {toc}{#1}{\ifnum #2>\c@secnumdepth \else
        \protect\numberline{\csname the#1\endcsname.}\fi
         #7}}\fi
     \@xsect{#5}}

\def\@xsect#1{\@tempskipa #1\relax
      \ifdim \@tempskipa>\z@
       \par \nobreak
       \addvspace{\@tempskipa}
       \@afterheading
    \else \global\@nobreakfalse \global\@noskipsectrue
       \everypar{\if@noskipsec \global\@noskipsecfalse
     \clubpenalty\@M \hskip -\parindent
     \begingroup \@svsechd \endgroup \unskip
     \hskip -#1
    \else       \clubpenalty \@clubpenalty
      \everypar{}\fi}\fi\ignorespaces}

% End of art10.sty


\def\labelenumi{\arabic{enumi}.}
\def\theenumi{\arabic{enumi}}
\def\labelenumii{(\alph{enumii})}
\def\theenumii{\alph{enumii}}
\def\p@enumii{\theenumi}
\def\labelenumiii{\roman{enumiii}.}
\def\theenumiii{\roman{enumiii}}
\def\p@enumiii{\theenumi(\theenumii)}
\def\labelenumiv{\Alph{enumiv}.}
\def\theenumiv{\Alph{enumiv}}
\def\p@enumiv{\p@enumiii\theenumiii}

\def\labelitemi{\bfseries --}
\def\labelitemii{\bfseries --}
\def\labelitemiii{$\bullet$}
\def\labelitemiv{$\cdot$}

\def\verse{\let\\=\@centercr
 \list{}{\itemsep\z@ \itemindent -1.5em\listparindent \itemindent
 \rightmargin\leftmargin\advance\leftmargin 1.5em}\item[]}
\let\endverse\endlist
\def\quotation{\list{}{\listparindent 1.5em
 \itemindent\listparindent
 \rightmargin\leftmargin \parsep 0pt plus 1pt}\item[]}
\let\endquotation=\endlist
\def\quote{\list{}{\rightmargin\leftmargin}\item[]}
\let\endquote=\endlist

\def\descriptionlabel#1{\hspace\labelsep \bfseries #1}
\def\description{\list{}{\labelwidth\z@ \itemindent-\leftmargin
 \let\makelabel\descriptionlabel}}
\let\enddescription\endlist


\def\theequation{\arabic{equation}}


\def\titlepage{\@restonecolfalse\if@twocolumn\@restonecoltrue\onecolumn
 \else \newpage \fi \thispagestyle{empty}\c@page\z@}
\def\endtitlepage{\if@restonecol\twocolumn \else \newpage \fi}

\arraycolsep 2.5pt \tabcolsep 6pt
\arrayrulewidth .4pt \doublerulesep 2pt
\tabbingsep \labelsep

\skip\@mpfootins = \skip\footins
\fboxsep = 3pt \fboxrule = .4pt

\newcounter{part}
\newcounter {section}
\newcounter {subsection}[section]
\newcounter {subsubsection}[subsection]
\newcounter {paragraph}[subsubsection]
\newcounter {subparagraph}[paragraph]

% Following commands have been adapted to produce (sub)section headings
% according to CAOSP layout (a period after each number).

\def\thepart{\Roman{part}} \def\thesection {\arabic{section}}
\def\thesubsection {\thesection.\arabic{subsection}}
\def\thesubsubsection {\thesubsection.\arabic{subsubsection}}
\def\theparagraph {\thesubsubsection.\arabic{paragraph}}
\def\thesubparagraph {\theparagraph.\arabic{subparagraph}}

\def\@pnumwidth{1.55em}
\def\@tocrmarg {2.55em}
\def\@dotsep{4.5}
\setcounter{tocdepth}{3}

\def\tableofcontents{\section*{\contentsname\markboth{\contentsname}
{\contentsname}}
 \@starttoc{toc}}
\def\l@part#1#2{\addpenalty{\@secpenalty}
 \addvspace{2.25em plus 1pt} \begingroup
 \@tempdima 3em \parindent \z@ \rightskip \@pnumwidth \parfillskip
-\@pnumwidth
 {\large \bfseries \leavevmode #1\hfil \hbox to\@pnumwidth{\hss #2}}\par
 \nobreak \endgroup}
\def\l@section#1#2{\addpenalty{\@secpenalty} \addvspace{1.0em plus 1pt}
\@tempdima 1.5em \begingroup
 \parindent \z@ \rightskip \@pnumwidth
 \parfillskip -\@pnumwidth
 \bfseries \leavevmode #1\hfil \hbox to\@pnumwidth{\hss #2}\par
 \endgroup}
\def\l@subsection{\@dottedtocline{2}{1.5em}{2.3em}}
\def\l@subsubsection{\@dottedtocline{3}{3.8em}{3.2em}}
\def\l@paragraph{\@dottedtocline{4}{7.0em}{4.1em}}
\def\l@subparagraph{\@dottedtocline{5}{10em}{5em}}
\def\listoffigures{\section*{\listfigurename\markboth
 {\listfigurename}{\listfigurename}}\@starttoc{lof}}
\def\l@figure{\@dottedtocline{1}{1.5em}{2.3em}}
\def\listoftables{\section*{\listtablename\markboth
 {\listtablename}{\listtablename}}\@starttoc{lot}}
\let\l@table\l@figure


% \list parameters have been adjusted in the `thebibliography'
% environment to the match CAOSP layout of References.
\def\thebibliography#1{\section*{\bibname\markboth
 {\bibname}{\bibname}}\small \list
% The \arabic{enumi} command has been removed because we don't use
% numbered citations in astronomical journals.
 {}{\setlength\labelwidth{1.4em}\leftmargin\labelwidth
 \setlength\parsep{0pt}\setlength\itemsep{0pt}
 \setlength{\itemindent}{-\leftmargin}
 \usecounter{enumi}}
 \def\newblock{\hskip .11em plus .33em minus -.07em}
 \sloppy
 \sfcode`\.=1000\relax}
\let\endthebibliography=\endlist

\def\article#1#2#3#4#5{\bibitem{} #1: #2, {{\itshape{#3}}}~{\bfseries{#4}}, #5\par}
%\article{author}{year}{journal}{volume}{page}
\def\book#1#2#3#4#5{\bibitem{} #1: #2, {{\itshape{#3}}}, #4, {#5}\par}
%\book{author}{year}{name}{publisher}{town}

\newcounter{@edia}
\newcounter{@edib}
\newif\if@eds
\def\pisa#1{\setcounter{@edib}{1}\def\and{\stepcounter{@edib}
                \ifnum\c@@edib=\c@@edia and \else \unskip, \fi} \unskip#1}
\def\sca#1{\setcounter{@edia}{1} \@edsfalse
           \def\and{\@edstrue \stepcounter{@edia}}\nullfont#1\small
           \if@eds eds.:~ \else ed.:~ \fi \pisa{#1}}
\def\inproceedings#1#2#3#4#5#6#7{\bibitem{} #1: #2, in~{{\itshape{#3}}}, \sca{#4},
 #5, #6, #7\par}
\def\urlref#1#2{\bibitem{} URL: #1, {\tt{#2}}\par}
%\urlref{title}{url}


\newif\if@restonecol
\def\theindex{\@restonecoltrue\if@twocolumn\@restonecolfalse\fi
\columnseprule \z@
\columnsep 35pt\twocolumn[\section*{\indexname}]
 \markboth{\indexname}{\indexname}\thispagestyle{plain}\parindent\z@
 \parskip\z@ plus .3pt\relax\let\item\@idxitem}
\def\@idxitem{\par\hangindent 40pt}
\def\subitem{\par\hangindent 40pt \hspace*{20pt}}
\def\subsubitem{\par\hangindent 40pt \hspace*{30pt}}
\def\endtheindex{\if@restonecol\onecolumn\else\clearpage\fi}
\def\indexspace{\par \vskip 10pt plus 5pt minus 3pt\relax}

\def\footnoterule{\kern-3\p@
 \hrule width 4.cm
 \kern 2.6\p@}

\long\def\@makefntext#1{\parindent 1em\noindent
 \hbox to 1.8em{\hss$^{\@thefnmark}$}#1}

\setcounter{topnumber}{2}
\def\topfraction{.9}
\setcounter{bottomnumber}{1}
\def\bottomfraction{.3}
\setcounter{totalnumber}{3}
\def\textfraction{.15}
\def\floatpagefraction{.85}
\setcounter{dbltopnumber}{2}
\def\dbltopfraction{.85}
\def\dblfloatpagefraction{.85}

% Captions of figures and tables
% Use \small lettering when in `table' or `figure' environment:
% Make sure that `Table <N>.' or `Figure <N>.' is typeset in boldface:

\newlength\abovecaptionskip
\newlength\belowcaptionskip
\setlength\abovecaptionskip{10\p@}
\setlength\belowcaptionskip{0\p@}

\def\fig@type{figure}
\def\tab@type{table}

\newdimen\figcapgap\figcapgap=8.pt 
\newdimen\tabcapgap\tabcapgap=4.pt

\@ifundefined{floatlegendstyle}{\def\floatlegendstyle{\bf}}{}
\def\floatcounterend{.}


\long\def\@makecaption#1#2{%
 \ifx\@captype\fig@type
   \vskip\figcapgap
 \fi
 \setbox\@tempboxa\hbox{\small {\bfseries{#1}} #2}
 \ifdim\wd\@tempboxa>\hsize 
  \unhbox\@tempboxa\par \vskip 8pt 
 \else 
  \hbox to\hsize{\hfil\box\@tempboxa\hfil} \vskip 8pt 
 \fi
 \ifx\@captype\tab@type
   \vskip\tabcapgap 
 \fi
 }

\if@referee
 \def\picplace#1{\hfil \fbox{FIGURE} \hfil}
 \def\insertplot#1#2#3{\hfil \fbox{FIGURE} \hfil}
\else
 \def\picplace#1{\vbox{\hrule\@height 0.4pt\@width\hsize
 \hbox to\hsize{\vrule\@width 0.4pt\@height#1\hfil
 \vrule\@width 0.4pt\@height#1}\hrule\@height 0.4pt\@width\hsize}}
 \def\insertplot#1#2#3{\par \hbox{ \hskip #3
              \vbox to #2{\special{em:graph #1} \vfil}}}
\fi

\newcounter{figure}
\def\thefigure{\@arabic\c@figure}
\def\fps@figure{htbp}
\def\ftype@figure{1}
\def\ext@figure{lof}
\def\fnum@figure{\figurename~\thefigure.}
\def\figure{\@float{figure}}
\let\endfigure\end@float
\@namedef{figure*}{\@dblfloat{figure}}
\@namedef{endfigure*}{\end@dblfloat}

\newcounter{table}
\def\thetable{\@arabic\c@table}
\def\fps@table{htbp}
\def\ftype@table{2}
\def\ext@table{lot}
\def\fnum@table{\tablename~\thetable.}
\def\table{\@float{table}}
\let\endtable\end@float
\@namedef{table*}{\@dblfloat{table}}
\@namedef{endtable*}{\end@dblfloat}

\def\volume#1{\gdef\@volume{#1}}
\gdef\@volume{?}
\def\volnumber#1{\gdef\@volnumber{#1}}
\gdef\@volnumber{?}
\def\pubyear#1{\gdef\@pubyear{#1}}
\gdef\@pubyear{\number\year}
% ak argumentom nie je kladny integer, nastavi 1, inak nastavi cislo z argumentu
%  https://tex.stackexchange.com/questions/7180/testing-for-number/208816
\def\firstpage#1{\if!\ifnum9<1#1!\else_\fi \gdef\@firstpage{#1} \c@page=0 \global\advance\c@page by #1 \else \gdef\@firstpage{1} \fi}
\gdef\@firstpage{1}
\def\lastpage#1{\gdef\@lastpage{#1}}
\gdef\@lastpage{?}
\def\originalfirstpage#1{\gdef\@originalfirstpage{#1}}
\gdef\@originalfirstpage{?}
\def\originallastpage#1{\gdef\@originallastpage{#1}}
\gdef\@originallastpage{?}
\def\received#1{\gdef\@pubdate{#1}}
\gdef\@pubdate{\@date}
\def\accepted#1{\gdef\@accepted{#1}}
\gdef\@accepted{?}
%\def\URLDAT{https://www.astro.sk/caosp/Eedition/FullTexts/vol{\@volume}no{\@volnumber}/pp{\@firstpage}-{\@lastpage}.dat/}
\RequirePackage[hyphens]{url}
\def\URLDAT{\small\url{https://www.astro.sk/caosp/Eedition/FullTexts/vol\@volume no\@volnumber/pp\@firstpage -\@lastpage .dat/}}


% LaTeX does not provide a command to enter the authors institute
% addresses. The \institute command is defined here.

\newcounter{@inst}
\newcounter{@auth}
\newdimen\instindent

\def\institute#1{\gdef\@institute{{\itshape{#1}}}}

\def\institutename{\par
 \begingroup
 \parindent=0pt
 \parskip=0pt
 \setcounter{@inst}{1}%
 \def\and{\vskip .05cm\par\stepcounter{@inst}%
          \noindent
          \hbox to\instindent{\hss$^{\the@inst}$\enspace}\ignorespaces}%
 \setbox0=\vbox{\def\thanks##1{}\@institute}
 \ifnum\c@@inst>9
  \relax\setbox0=\hbox{$^{88}$\enspace}%
 \else
  \setbox0=\hbox{$^{8}$\enspace}%
 \fi
 \instindent=\wd0\relax
 \ifnum\c@@inst=1
  \relax
 \else
  \setcounter{@inst}{1}%
  \hangindent\instindent
  \noindent
  \hbox to\instindent{\hss$^{\the@inst}$\kern-3.5pt\enspace}\ignorespaces%
 \fi
 \ignorespaces
 \@institute\par
 \endgroup}


\def\offprints#1{\begingroup
\def\protect{\noexpand\protect\noexpand}\xdef\@thanks{\@thanks
\protect\footnotetext[0]{\unskip{{\itshape{Send offprint requests
to\/}}}: \ignorespaces#1}}\endgroup\ignorespaces}

\def\@thanks{}

\long\def\@makefntext#1{\parindent 1em\noindent
$^{\@thefnmark}$#1}

\def\@fnsymbol#1{\ifcase#1\or\star\or{\star\star}\or{\star\star\star}%
   \or \dagger\or \ddagger\or
   \mathchar "278\or \mathchar "27B\or \|\or **\or \dagger\dagger
   \or \ddagger\ddagger \else\@ctrerr\fi\relax}

\def\inst#1{\unskip$^{#1}$}

\def\subtitle#1{\gdef\@subtitle{#1}}
\def\@subtitle{}

\def\thesaurus#1{\gdef\@thesaurus{#1}}
\def\@thesaurus{missing; you have not inserted them}%

\def\journalname#1{\gdef\@journalname{#1}}
\gdef\@journalname{Contributions of the Astronomical Observatory Skalnat\'{e} Pleso}

\def\email#1{(E-mail: #1)}

% https://orcid.org/
%\def\orcid#1{ORCID #1}
\@ifpackageloaded{hyperref}%
{}{\RequirePackage[pdfpagelabels=false,colorlinks=true,linkcolor=blue,citecolor=blue,filecolor=blue,urlcolor=blue]{hyperref}
}%
%%%%%%%%%%%%%%%%%%%%%%%%%%% Macro ORCID %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%\def\orcid#1{}
\def\orcid#1{\unskip\protect\href{https://orcid.org/#1}{\protect$^{\includegraphics[width=8pt,clip]{logo_orcid}}$}}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\def\lomnica{Astronomical Institute of the Slovak Academy of Sciences\\
             059\,60 Tatransk\'{a} Lomnica, The Slovak Republic}
\def\ondrejov{Astronomical Institute of the Czech Academy of Sciences\\
              251\,65~Ond\v{r}ejov, The Czech Republic}
\def\blava{Astronomical Institute of the Slovak Academy of Sciences,
           Interplanetary Matter Division, D\'{u}bravsk\'{a} cesta 9,
           845\,04~Bratislava, The Slovak Republic}
\def\htitle#1{\gdef\@htitle{#1}}
\def\@htitle{\@title}%
\def\hauthor#1{\gdef\@hauthor{#1}}
\def\@hauthor{}%
\def\articleNo#1{\gdef\@articleNo{#1}}
\def\@articleNo{.....}%
\def\maketitle{\par
 \ch@ckobl{journalname}{Noname}
 \ch@ckobl{date}{the date of receipt and acceptance should be inserted later}
 \ch@ckobl{title}{A title should be given}
 \ch@ckobl{author}{Name(s) and initial(s) of author(s) should be given}
 \ch@ckobl{institute}{Address(es) of author(s) should be given}
 \begingroup
 \def\thefootnote{\fnsymbol{footnote}}
 \if@twocolumn
   \twocolumn[\@maketitle]
 \else
   \newpage \@maketitle
 \fi
 \global\@topnum\z@
 \thispagestyle{empty}\@thanks
 \endgroup
 \ps@myheadings \caomarkboth
 \setcounter{footnote}{0}
 \let\maketitle\relax
 \let\@maketitle\relax
 \gdef\@thanks{}\gdef\@author{}\gdef\@title{}\gdef\@subtitle{}\gdef\@aur{}%

 \let\thanks\relax}

%%%%%%%%%%%%%Journal Logo
\def\caospb{\setbox254=\hbox{of the Astronomical Observatory}%
\vbox{\baselineskip=10dd\hrule\hbox{%\vrule
\vbox{\kern3pt
\hbox to\wd254{\hfil Contributions \hfil}
\copy254
\hbox to\wd254{\hfil Skalnat\'{e} Pleso\hfil}
\kern3pt}%\vrule
}\hrule}}

\def\makeheadbox
 {\if@supplement
   \kern-22.pt
  \fi
  \if@referee
   \kern15pt
  \fi
  {\hsize=25cc \hbox to0pt
   {\vbox
    {\baselineskip=8dd
     \hbox to\hsize
      {\kern0pt
       \vbox
        {\kern7pt
         \hbox
          {\kern0pt
           \if@referee
            Contrib. Astron. Obs. Skalnat\'{e} Pleso -- 
             {\bfseries{Referee version}}, article No.\,{\@articleNo}%%%
           \else
            \if@errata
              Contrib. Astron. Obs. Skalnat\'{e} Pleso -- 
              {\bfseries{Errata: {\@volume}/{\@volnumber}}}, \@originalfirstpage\,--\,\@originallastpage, (\@pubyear)\hfill%%%
            \else 
              \vbox{ 
                    \hbox{Contrib. Astron. Obs. Skalnat\'{e} Pleso
                     {\bfseries{\@volume}/{\@volnumber}}, \@firstpage\,--\,\@lastpage, (\@pubyear)\hfill}%%%%%
                    \newcounter{prvastrana}
                    \setcounter{prvastrana}{\@firstpage}
                    \ifnum\value{prvastrana}>1
                     %\hbox{DOI:\,10.31577/caosp.\@pubyear.\@volume.\@volnumber.\@firstpage}%%%%%
                     \hbox{https://doi.org/10.31577/caosp.\@pubyear.\@volume.\@volnumber.\@firstpage\hfill}%%%%%
                    \else
                      \hbox{DOI:\,to be assigned later\hfill}%%%%%
                    \fi
                   }
            \fi
           \fi
           \kern0pt
          }
         \hrule
         \kern5pt
        } 
       \hfil
      }
    }
%\hbox{~}
%\hbox{\rightskip=0pt plus3em\advance\hsize by-7pt \vbox{~}}
%  \kern3pt}\hfil\kern3pt}}
%\rlap{\quad\caospb}
    \hss
   }
  }
 }
%%%%%%%%%%%%%Journal Logo

\def\caomarkboth{\markboth{\@hauthor}{\@htitle}
 \def\markboth{\@gobbletwo}}

\def\@maketitle{\newpage
 \if@supplement
  \ifodd\c@page
   {\begin{picture}(0,0)(\okrajtitulpravyx,\okrajtitulpravyy)\pasik\end{picture}}
  \else
   {\begin{picture}(0,0)(\okrajtitullavyx,\okrajtitullavyy)\pasik\end{picture}}
  \fi
 \fi
\begin{center}
 \rm\vbox to0pt{}\vskip-18mm
 \makeheadbox
 \vskip5.mm
 {\Large \bfseries\unboldmath
  \pretolerance=10000
  \noindent\ignorespaces
  \@title \par}\vskip .3cm
\if!\@subtitle!\else {\large \bfseries\unboldmath
  \vskip .05cm
  \pretolerance=10000
  \noindent\@subtitle \par}\vskip .4cm\fi
 {\bfseries \lineskip .5em
\setbox0=\vbox{\setcounter{@auth}{1}\def\and{\stepcounter{@auth}}%
\def\thanks##1{}\@author\global\c@@inst=\c@@auth}%
\def\lastand{\ifnum\c@@inst=2\relax\unskip{} and \else
\unskip ~and \fi}%
\setcounter{@auth}{1}%
\def\and{\stepcounter{@auth}\ifnum\c@@auth=\c@@inst\lastand\else
\unskip, \fi}%
 \noindent\@author\vskip.125cm}
 \institutename
 \if@supplement
  \vskip .35cm {\normalsize\noindent Received:~\@pubdate}
 \else 
  \if@errata
   \vskip .35cm {\normalsize\noindent Received:~\@pubdate}
  \else
   \vskip .35cm {\normalsize\noindent Received:~\@pubdate; Accepted:~\@accepted}
  \fi
 \fi 
%%%%%%%%%%%%%Journal Logo - old
%\if@referee
% \footnotetext{Contrib. Astron. Obs. Skalnat\'{e} Pleso -- {\bfseries{Referee version}}}
%\else
% \footnotetext{Contrib. Astron. Obs. Skalnat\'{e} Pleso
%   {\bfseries{\@volume}}, (\@pubyear), \@firstpage\,--\,\@lastpage.}
%\fi
%%%%%%%%%%%%%Journal Logo - old
 \par
 \vskip -.25cm\end{center}}


\def\abstractnameh{\par\vspace{5.pt}\noindent{\bfseries{\abstractname.}}}
\def\abstract{\if@twocolumn
\section*{\abstractnameh}
\else \small
\quotation \abstractnameh
\fi}
\def\endabstract{\vspace{5.pt}\if@twocolumn\else\endquotation\fi}
\mark{{}{}}

% Define \keywords

\def\keywords{\par\vspace{1.pt}\noindent{\bfseries{\keywordsname:} }}

\if@twoside
\def\ps@headings{\def\@oddfoot{}\def\@evenfoot{}
 \def\@evenhead{
  \if@supplement
   {\begin{picture}(0,0)(\okrajlavyx,\okrajlavyy)\pasik\end{picture}}
  \fi
 \rm\thepage\hfil \sl \leftmark}
 \def\@oddhead{
  \if@supplement
   {\begin{picture}(0,0)(\okrajpravyx,\okrajpravyy)\pasik\end{picture}}
  \fi
 \hbox{}\sl \rightmark \hfil\rm\thepage}
\def\sectionmark##1{\markboth {\uppercase{\ifnum
\c@secnumdepth >\z@ \thesection\hskip 1em\relax \fi
##1}}{}}\def\subsectionmark##1{\markright {\ifnum \c@secnumdepth >\@ne
\thesubsection\hskip 1em\relax \fi ##1}}}
\else
\def\ps@headings{\def\@oddfoot{}\def\@evenfoot{}
 \def\@oddhead{
  \if@supplement
   {\begin{picture}(0,0)(\okrajpravyx,\okrajpravyy)\pasik\end{picture}}
  \fi
 \hbox{}\sl \rightmark \hfil \rm\thepage}\def\sectionmark##1{\markright
{\uppercase{\ifnum \c@secnumdepth >\z@ \thesection\hskip 1em\relax \fi
##1}}}}
\fi
\def\ps@myheadings{
 \def\@oddhead{
 \if@supplement
  {\begin{picture}(0,0)(\okrajpravyx,\okrajpravyy)\pasik\end{picture}}
  \kern-2.pt{\scriptsize\rightmark}\hfil\kern8.pt\rm\thepage
 \else
  \if@errata
   {\scriptsize\rightmark}\hfil\rm{E\thepage}
  \else
   {\scriptsize\rightmark}\hfil\rm\thepage
  \fi
 \fi
              }
 \def\@oddfoot{}
 \def\@evenhead{
  \if@supplement
   {\begin{picture}(0,0)(\okrajlavyx,\okrajlavyy)\pasik\end{picture}}
   \kern-8.pt\rm\thepage\hfil{\scriptsize\leftmark}
  \else
   \if@errata
    \kern-4.pt\rm{E\thepage}\hfil{\scriptsize\leftmark}
   \else 
    \kern-4.pt\rm\thepage\hfil{\scriptsize\leftmark}
   \fi
  \fi
               }
  \def\@evenfoot{}
  \def\sectionmark##1{}
  \def\subsectionmark##1{}
                  }


\def\today{\ifcase\month\or
 January\or February\or March\or April\or May\or June\or
 July\or August\or September\or October\or November\or December\fi
 \space\number\day, \number\year}

%\ps@myheadings \pagenumbering{arabic} \onecolumn
%\if@twoside\else\raggedbottom\fi
\ps@plain \pagenumbering{arabic} \onecolumn \if@twoside\else\raggedbottom\fi


\def\@array[#1]#2{\setbox\@arstrutbox=\hbox{\vrule
     height\arraystretch \ht\strutbox
     depth\arraystretch \dp\strutbox
     width\z@}\@mkpream{@{}#2}\edef\@preamble{\halign \noexpand\@halignto
\bgroup \tabskip\z@ \@arstrut \@preamble \tabskip\z@ \cr}%
\let\@startpbox\@@startpbox \let\@endpbox\@@endpbox
  \if #1t\vtop \else \if#1b\vbox \else \vcenter \fi\fi
  \bgroup \let\par\relax
  \let\@sharp##\let\protect\relax \lineskip\z@\baselineskip\z@\@preamble}



% Define \acknowledgements

\def\acknowledgements{\vspace{12pt}\noindent{\bfseries{\acknowname.\/} }\small%
\ignorespaces}

% Redefine \@cite so no square brackets are output.
% Redefine \@biblabel so the label is not output in the bibliography.

\def\@cite#1#2{{#1\if@tempswa , #2\fi}}
\def\@biblabel#1{}

\def\squareforqed{\hbox{\rlap{$\sqcap$}$\sqcup$}}
\def\sq{\ifmmode\squareforqed\else{\unskip\nobreak\hfil
\penalty50\hskip1em\null\nobreak\hfil\squareforqed
\parfillskip=0pt\finalhyphendemerits=0\endgraf}\fi}

\def\sun{\hbox{$\odot$}}
\def\la{\mathrel{\mathchoice {\vcenter{\offinterlineskip\halign{\hfil
$\displaystyle##$\hfil\cr<\cr\sim\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\textstyle##$\hfil\cr
<\cr\sim\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptstyle##$\hfil\cr
<\cr\sim\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptscriptstyle##$\hfil\cr
<\cr\sim\cr}}}}}
\def\ga{\mathrel{\mathchoice {\vcenter{\offinterlineskip\halign{\hfil
$\displaystyle##$\hfil\cr>\cr\sim\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\textstyle##$\hfil\cr
>\cr\sim\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptstyle##$\hfil\cr
>\cr\sim\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptscriptstyle##$\hfil\cr
>\cr\sim\cr}}}}}
\def\softd{{\leavevmode\setbox1=\hbox{d}\hbox to 1.05\wd1{d\kern-0.4ex{\char039}\hss}}}
\def\softt{{\leavevmode\setbox1=\hbox{t}\hbox to \wd1{t\kern-0.6ex{\char039}\hss}}}
\def\softl{l\kern-0.45ex\raise0.1ex\hbox{'}\kern-0.10ex}
\def\softL{L\kern-0.8ex\raise0.1ex\hbox{'}\kern0.1ex}   
\def\angstrom{\AA}
\def\degr{\hbox{$^\circ$}}
\def\arcmin{\hbox{$^\prime$}}
\def\arcsec{\hbox{$^{\prime\prime}$}}
\def\utw{\smash{\rlap{\lower5pt\hbox{$\sim$}}}}
\def\udtw{\smash{\rlap{\lower6pt\hbox{$\approx$}}}}
\def\fd{\hbox{$.\!\!^{\rm d}$}}
\def\fh{\hbox{$.\!\!^{\rm h}$}}
\def\fm{\hbox{$.\!\!^{\rm m}$}}
\def\fs{\hbox{$.\!\!^{\rm s}$}}
\def\fdg{\hbox{$.\!\!^\circ$}}
\def\farcm{\hbox{$.\mkern-4mu^\prime$}}
\def\farcs{\hbox{$.\!\!^{\prime\prime}$}}
\def\fp{\hbox{$.\!\!^{\scriptscriptstyle\rm p}$}}
\def\cor{\mathrel{\mathchoice {\hbox{$\widehat=$}}{\hbox{$\widehat=$}}
{\hbox{$\scriptstyle\hat=$}}
{\hbox{$\scriptscriptstyle\hat=$}}}}
\def\sol{\mathrel{\mathchoice {\vcenter{\offinterlineskip\halign{\hfil
$\displaystyle##$\hfil\cr\sim\cr<\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\textstyle##$\hfil\cr\sim\cr
<\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptstyle##$\hfil\cr\sim\cr
<\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptscriptstyle##$\hfil\cr
\sim\cr<\cr}}}}}
\def\sog{\mathrel{\mathchoice {\vcenter{\offinterlineskip\halign{\hfil
$\displaystyle##$\hfil\cr\sim\cr>\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\textstyle##$\hfil\cr\sim\cr
>\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptstyle##$\hfil\cr
\sim\cr>\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptscriptstyle##$\hfil\cr
\sim\cr>\cr}}}}}
\def\lse{\mathrel{\mathchoice {\vcenter{\offinterlineskip\halign{\hfil
$\displaystyle##$\hfil\cr<\cr\simeq\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\textstyle##$\hfil\cr
<\cr\simeq\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptstyle##$\hfil\cr
<\cr\simeq\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptscriptstyle##$\hfil\cr
<\cr\simeq\cr}}}}}
\def\gse{\mathrel{\mathchoice {\vcenter{\offinterlineskip\halign{\hfil
$\displaystyle##$\hfil\cr>\cr\simeq\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\textstyle##$\hfil\cr
>\cr\simeq\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptstyle##$\hfil\cr
>\cr\simeq\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptscriptstyle##$\hfil\cr
>\cr\simeq\cr}}}}}
\def\grole{\mathrel{\mathchoice {\vcenter{\offinterlineskip\halign{\hfil
$\displaystyle##$\hfil\cr>\cr\noalign{\vskip-1.5pt}<\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\textstyle##$\hfil\cr
>\cr\noalign{\vskip-1.5pt}<\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptstyle##$\hfil\cr
>\cr\noalign{\vskip-1pt}<\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptscriptstyle##$\hfil\cr
>\cr\noalign{\vskip-0.5pt}<\cr}}}}}
\def\leogr{\mathrel{\mathchoice {\vcenter{\offinterlineskip\halign{\hfil
$\displaystyle##$\hfil\cr<\cr\noalign{\vskip-1.5pt}>\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\textstyle##$\hfil\cr
<\cr\noalign{\vskip-1.5pt}>\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptstyle##$\hfil\cr
<\cr\noalign{\vskip-1pt}>\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptscriptstyle##$\hfil\cr
<\cr\noalign{\vskip-0.5pt}>\cr}}}}}
\def\loa{\mathrel{\mathchoice {\vcenter{\offinterlineskip\halign{\hfil
$\displaystyle##$\hfil\cr<\cr\approx\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\textstyle##$\hfil\cr
<\cr\approx\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptstyle##$\hfil\cr
<\cr\approx\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptscriptstyle##$\hfil\cr
<\cr\approx\cr}}}}}
\def\goa{\mathrel{\mathchoice {\vcenter{\offinterlineskip\halign{\hfil
$\displaystyle##$\hfil\cr>\cr\approx\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\textstyle##$\hfil\cr
>\cr\approx\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptstyle##$\hfil\cr
>\cr\approx\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptscriptstyle##$\hfil\cr
>\cr\approx\cr}}}}}
\def\diameter{{\ifmmode\mathchoice
{\ooalign{\hfil\hbox{$\displaystyle/$}\hfil\crcr
{\hbox{$\displaystyle\mathchar"20D$}}}}
{\ooalign{\hfil\hbox{$\textstyle/$}\hfil\crcr
{\hbox{$\textstyle\mathchar"20D$}}}}
{\ooalign{\hfil\hbox{$\scriptstyle/$}\hfil\crcr
{\hbox{$\scriptstyle\mathchar"20D$}}}}
{\ooalign{\hfil\hbox{$\scriptscriptstyle/$}\hfil\crcr
{\hbox{$\scriptscriptstyle\mathchar"20D$}}}}
\else{\ooalign{\hfil/\hfil\crcr\mathhexbox20D}}%
\fi}}


\def\getsto{\mathrel{\mathchoice {\vcenter{\offinterlineskip
\halign{\hfil
$\displaystyle##$\hfil\cr\gets\cr\to\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\textstyle##$\hfil\cr\gets
\cr\to\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptstyle##$\hfil\cr\gets
\cr\to\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptscriptstyle##$\hfil\cr
\gets\cr\to\cr}}}}}
\def\lid{\mathrel{\mathchoice {\vcenter{\offinterlineskip\halign{\hfil
$\displaystyle##$\hfil\cr<\cr\noalign{\vskip1.2pt}=\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\textstyle##$\hfil\cr<\cr
\noalign{\vskip1.2pt}=\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptstyle##$\hfil\cr<\cr
\noalign{\vskip1pt}=\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptscriptstyle##$\hfil\cr
<\cr
\noalign{\vskip0.9pt}=\cr}}}}}
\def\gid{\mathrel{\mathchoice {\vcenter{\offinterlineskip\halign{\hfil
$\displaystyle##$\hfil\cr>\cr\noalign{\vskip1.2pt}=\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\textstyle##$\hfil\cr>\cr
\noalign{\vskip1.2pt}=\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptstyle##$\hfil\cr>\cr
\noalign{\vskip1pt}=\cr}}}
{\vcenter{\offinterlineskip\halign{\hfil$\scriptscriptstyle##$\hfil\cr
>\cr
\noalign{\vskip0.9pt}=\cr}}}}}
\def\bbbr{{\rm I\!R}} %reelle Zahlen
\def\bbbm{{\rm I\!M}}
\def\bbbn{{\rm I\!N}} %natuerliche Zahlen
\def\bbbf{{\rm I\!F}}
\def\bbbh{{\rm I\!H}}
\def\bbbk{{\rm I\!K}}
\def\bbbp{{\rm I\!P}}
\def\bbbone{{\mathchoice {\rm 1\mskip-4mu l} {\rm 1\mskip-4mu l}
{\rm 1\mskip-4.5mu l} {\rm 1\mskip-5mu l}}}
\def\bbbc{{\mathchoice {\setbox0=\hbox{$\displaystyle\rm C$}\hbox{\hbox
to0pt{\kern0.4\wd0\vrule height0.9\ht0\hss}\box0}}
{\setbox0=\hbox{$\textstyle\rm C$}\hbox{\hbox
to0pt{\kern0.4\wd0\vrule height0.9\ht0\hss}\box0}}
{\setbox0=\hbox{$\scriptstyle\rm C$}\hbox{\hbox
to0pt{\kern0.4\wd0\vrule height0.9\ht0\hss}\box0}}
{\setbox0=\hbox{$\scriptscriptstyle\rm C$}\hbox{\hbox
to0pt{\kern0.4\wd0\vrule height0.9\ht0\hss}\box0}}}}
\def\bbbq{{\mathchoice {\setbox0=\hbox{$\displaystyle\rm
Q$}\hbox{\raise
0.15\ht0\hbox to0pt{\kern0.4\wd0\vrule height0.8\ht0\hss}\box0}}
{\setbox0=\hbox{$\textstyle\rm Q$}\hbox{\raise
0.15\ht0\hbox to0pt{\kern0.4\wd0\vrule height0.8\ht0\hss}\box0}}
{\setbox0=\hbox{$\scriptstyle\rm Q$}\hbox{\raise
0.15\ht0\hbox to0pt{\kern0.4\wd0\vrule height0.7\ht0\hss}\box0}}
{\setbox0=\hbox{$\scriptscriptstyle\rm Q$}\hbox{\raise
0.15\ht0\hbox to0pt{\kern0.4\wd0\vrule height0.7\ht0\hss}\box0}}}}
\def\bbbt{{\mathchoice {\setbox0=\hbox{$\displaystyle\rm
T$}\hbox{\hbox to0pt{\kern0.3\wd0\vrule height0.9\ht0\hss}\box0}}
{\setbox0=\hbox{$\textstyle\rm T$}\hbox{\hbox
to0pt{\kern0.3\wd0\vrule height0.9\ht0\hss}\box0}}
{\setbox0=\hbox{$\scriptstyle\rm T$}\hbox{\hbox
to0pt{\kern0.3\wd0\vrule height0.9\ht0\hss}\box0}}
{\setbox0=\hbox{$\scriptscriptstyle\rm T$}\hbox{\hbox
to0pt{\kern0.3\wd0\vrule height0.9\ht0\hss}\box0}}}}
\def\bbbs{{\mathchoice
{\setbox0=\hbox{$\displaystyle     \rm S$}\hbox{\raise0.5\ht0\hbox
to0pt{\kern0.35\wd0\vrule height0.45\ht0\hss}\hbox
to0pt{\kern0.55\wd0\vrule height0.5\ht0\hss}\box0}}
{\setbox0=\hbox{$\textstyle        \rm S$}\hbox{\raise0.5\ht0\hbox
to0pt{\kern0.35\wd0\vrule height0.45\ht0\hss}\hbox
to0pt{\kern0.55\wd0\vrule height0.5\ht0\hss}\box0}}
{\setbox0=\hbox{$\scriptstyle      \rm S$}\hbox{\raise0.5\ht0\hbox
to0pt{\kern0.35\wd0\vrule height0.45\ht0\hss}\raise0.05\ht0\hbox
to0pt{\kern0.5\wd0\vrule height0.45\ht0\hss}\box0}}
{\setbox0=\hbox{$\scriptscriptstyle\rm S$}\hbox{\raise0.5\ht0\hbox
to0pt{\kern0.4\wd0\vrule height0.45\ht0\hss}\raise0.05\ht0\hbox
to0pt{\kern0.55\wd0\vrule height0.45\ht0\hss}\box0}}}}
\def\bbbz{{\mathchoice {\hbox{$\sf\textstyle Z\kern-0.4em Z$}}
{\hbox{$\sf\textstyle Z\kern-0.4em Z$}}
{\hbox{$\sf\scriptstyle Z\kern-0.3em Z$}}
{\hbox{$\sf\scriptscriptstyle Z\kern-0.2em Z$}}}}
\def\ts{\thinspace}

\def\typeset{\vfill{\small\noindent This article was processed by the
author using  \LaTeX\ CAOSP style file 1992.\par}}

\def\enddocument{\par%\typeset
\@checkend{document}\clearpage\begingroup
\addtocounter{page}{-1}\immediate\write\@mainaux{\string\lastpage{\thepage}}
\if@filesw \immediate\closeout\@mainaux
%\def\global\@namedef##1##2{}\def\newlabel{\@testdef r}%
\def\@namedef##1##2{}\def\newlabel{\@testdef r}%
\def\bibcite{\@testdef b}\@tempswafalse\makeatletter\input \jobname.aux
\if@tempswa \@warning{Label(s) may have changed. Rerun to get
cross-references right}\fi\fi\endgroup\deadcycles\z@\@@end}


\newcommand{\cm}{\ {\rm cm}}
\newcommand{\mG}{\ {\rm mG}}
\newcommand{\dyn}{\ {\rm dyn}}
\newcommand{\erg}{\ {\rm erg}}
\newcommand{\kpc}{\ {\rm kpc}}
\newcommand{\yr}{\ {\rm yr}}
\newcommand{\secnd}{\ {\rm s}}
\newcommand{\Msol}{M_{\odot}}
%
%  references
%


\newcommand{\abasb}		{Abastumani Bull.}					% Abastumani Bulletin
\newcommand{\aaa}		{Astronomy and Astrophysics}				% Astronomy and Astrophysics
\newcommand{\aaas}		{Astronomy and Astrophysics, Supplement Series}		% Astronomy and Astrophysics, Supplement Series
%\newcommand{\aap}		{Astronomy and Astrophysics}				% Astronomy & Astrophysics
%\newcommand{\aapr}		{Astronomy and Astrophysics Reviews}			% Astronomy & Astrophysics Reviews
%\newcommand{\aaps}		{Astronomy and Astrophysics, Supplement}		% Astronomy & Astrophysics, Supplement
\newcommand{\aas}		{Acta Astron. Sinica}					% Acta Astronomica Sinica
\newcommand{\aca}		{Acta Astron.}						% Acta Astronomica
\newcommand{\aipconf}		{Amer. Inst. Phys. Conf. Proc.}				% American Institute of Physics Conference Proceedings
%\newcommand{\aj}		{Astron. J.}						% Astronomical Journal
\newcommand{\an}		{Astronomische Nachrichten}				% Astronomische Nachrichten
%\newcommand{\ao}		{Applied Optics}					% Applied Optics
%\newcommand{\apj}		{Astrophysical Journal}					% Astrophysical Journal
%\newcommand{\apjl}		{Astrophysical Journal, Letters}			% Astrophysical Journal, Letters
\newcommand{\apjlett}	        {Astrophysical Journal, Letters}			% The Astrophysical Journal, Letters
%\newcommand{\apjs}		{Astrophysical Journal, Supplement}			% The Astrophysical Journal, Supplement
\newcommand{\apjss}		{Astrophys. J., Suppl. Ser.}				% Astrophysical Journal, Supplement Series
\newcommand{\apjsupp}		{Astrophys. J., Suppl.}					% The Astrophysical Journal, Supplement
%\newcommand{\aplett}		{Astrophysics Letters}					% Astrophysics Letters
\newcommand{\applopt}		{Appl. Opt.}						% Applied Optics
%\newcommand{\apspr}		{Astrophysics Space Physics Research}			% Astrophysics Space Physics Research
%\newcommand{\apss}		{Astrophysics and Space Science}			% Astrophysics and Space Science
\newcommand{\ar}		{Ann. Rev. Astron. Astrophys.}				% Annual Review of Astronomy and Astrophysics
%\newcommand{\araa}		{Ann. Rev. Astron. Astrophys.}				% Annual Review of Astronomy & Astrophysics
\newcommand{\aspconf}	 	{ASP Conf. Ser.}					% Astronomical Society of the Pacific Conference Series
\newcommand{\asr}		{Adv. Space Res.}					% Advances in Space Research
\newcommand{\asslconf}		{Astrophys. Space Sien. Lib. Conf. Ser.}		% Astrophysics & Space Science Library Conference Series
\newcommand{\astap}		{Astron. Astrophys.}					% Astronomy & Astrophysics
%\newcommand{\azh}		{Astronomicheskii Zhurnal}				% Astronomicheskii Zhurnal
%\newcommand{\baas}		{Bulletin of the AAS}					% Bulletin of the American Astronomical Society
\newcommand{\bac}		{Bulletin Astronomical Institutes of Czechoslovakia}	% Bulletin of the Astronomical Institutes of Czechoslovakia
%\newcommand{\bain}		{Bulletin Astronomical Institute of the Netherlands}	% Bulletin of the Astronomical Instutes of Netherlands
\newcommand{\basi}		{Bull. Astron. Soc. India}				% Bulletin of the Astronical Society of India
%\newcommand{\caa}		{Chinese Astronomy and Astrophysics}			% Chinese Astronomy & Astrophysics
\newcommand{\caos}		{Contrib. Astron. Obs. Skalnat\'{e} Pleso}		% Contributions of the Astronomical Observatory Skalnate Pleso
\newcommand{\cpuo}		{Contrib. Princeton Univ. Obs.}				% Contributions Princeton University Observatory
\newcommand{\emp}		{Earth, Moon, Planets}					% Earth, Moon, Planets
%\newcommand{\fcp}		{Fundamental Cosmic Physics}				% Fundamental Cosmic Physics
\newcommand{\harva}		{Harvard Ann.}						% Harvard Annales
\newcommand{\harvc}		{Harvard Circ.}						% Harvard Circular
\newcommand{\iauc}		{IAU Circular}						% IAU Circular
%\newcommand{\iaucirc}	        {IAU Circulars}						% IAU Circulars
\newcommand{\iaut}		{IAU Trans.}	
\newcommand{\ibvs}		{Inf. Bull. Variable Stars}				% Information Bulletin on Variable Stars
\newcommand{\ica}		{Icarus}						% Icarus
%\newcommand{\jrasc}		{Journal of the RAS of Canada}				% Journal of the Royal Astronomical Society of Canada
\newcommand{\jrcan}		{Journal of the RAS of Canada}				% Journal of the Royal Astronomical Society of Canada
\newcommand{\krym}		{Izv. Krymskoj Astrofiz. Obs.}				% Izvestya Krymskoj Astrofizicheskoj Observatorii
\newcommand{\lickb}		{Lick Bull.}						% Lick Bulletin
\newcommand{\maps}		{Met. Planet. Sci.}					% Meteoritics & Planetary Science
%\newcommand{\memras}	        {Memoirs of the RAS}					% Memoirs of the Royal Astronomical Society
%\newcommand{\mnras}		{Monthly Notices of the RAS}				% Monthly Notices of the Royal Astronomical Society
\newcommand{\mpci}		{Minor Planet Circ.}					% Minor Planet Circulars
\newcommand{\mras}		{Memoirs of the RAS}					% Memoirs Royal Astron. Society
\newcommand{\msai}		{Mem. Soc. Astron. Ital.}				% Memoirs della Societa Astronomica Italiana
\newcommand{\mvs}		{Mitt. Verand. Sterne}					% Mitteilungen Verand. Sterne
%\newcommand{\nat}		{Nature}						% Nature
\newcommand{\obs}		{Observatory}						% The Observatory
\newcommand{\odesai}		{Odessa Izv.}						% Odessa Izvestija
\newcommand{\paics}		{Publ. Astron. Inst. Czechosl. Acad. Sci.}		% Publications of the Astronomical Institute of the Czechoslovak Academy of Sciences
%\newcommand{\pasj}		{Publications of the ASJ}				% Publications of the Astronomical Society of Japan
%\newcommand{\pasp}		{Publications of the ASP}				% Publ. of the Astron. Society of the Pacific
\newcommand{\pdao}		{Publ. DAO}						% Publications of DAO
\newcommand{\perzve}		{Perem. Zvezdy}						% Peremennye Zvezdy
%\newcommand{\planss}		{Planetary Space Science}				% Planetary Space Science
%\newcommand{\pra}		{Physical Review A: General Physics}			% Physical Review A: Atomic, Molecular, and Optical Physics
%\newcommand{\prb}		{Physical Review B: Solid State}			% Physical Review B: Condensed Matter and Materials Physics
%\newcommand{\prc}		{Physical Review C}					% Physical Review C: Nuclear Physics
%\newcommand{\prd}		{Physical Review D}					% Physical Review D: Particles, Fields, Gravitation and Cosmology
%\newcommand{\pre}		{Physical Review E}					% Physical Review E: Statistical, Nonlinear, and Soft Matter Physics
%\newcommand{\prl}		{Physical Review Letters}				% Physical Review Letters
%\newcommand{\procspie}		{Proceedings of the SPIE}				% Proceedings of the International Society for Optical Engineering
\newcommand{\pss}		{Planet. Space Sci.}					% Planetary and Space Science
%\newcommand{\qjras}		{Quarterly Journal of the RAS}				% Quarterly Journal of the Royal Astronomical Society
\newcommand{\rmaa}		{Rev. Mex. Astron. Astrofis.}				% Revista Mexicana de Astronomia y Astrofisica.
\newcommand{\rmp}		{Rev. Mod. Phys.}					% Reviews of Modern Physics
\newcommand{\sal}		{Sov. Astron. Lett.}					% Soviet Astronomy Letters
\newcommand{\sci}		{Science}						% Science
\newcommand{\sdan}		{Sol. dannye}						% Solnechnye dannye
%\newcommand{\skytel}		{Sky and Telescope}					% Sky & Telescope
%\newcommand{\solphys}	        {Solar Physics}						% Solar Physics
\newcommand{\sonnv}		{Sonnenberg Veroff.}					% Sonnenberg Veroff.
\newcommand{\sph}		{Solar Physics}						% Solar Physics
%\newcommand{\ssr}		{Space Science Reviews}					% Space Science Reviews
\newcommand{\va}		{Vistas Astron.}					% Vistas in Astronomy
% ----------------abbreviations used by ADS bibTeX------------------------------------
%  http://cdsads.u-strasbg.fr/abs_doc/aas_macros.html
%  http://ads.harvard.edu/pubs/bibtex/
\newcommand{\aj}              {Astronomical Journal}
\newcommand{\actaa}           {Acta Astronomica}
\newcommand{\araa}            {Annual Review of Astron and Astrophys}
\newcommand{\apj}             {Astrophysical Journal}
\newcommand{\apjl}            {Astrophysical Journal, Letters}
\newcommand{\apjs}            {Astrophysical Journal, Supplement}
\newcommand{\ao}              {Applied Optics}
\newcommand{\apss}            {Astrophysics and Space Science}
\newcommand{\aap}             {Astronomy and Astrophysics}
\newcommand{\aapr}            {Astronomy and Astrophysics Reviews}
\newcommand{\aaps}            {Astronomy and Astrophysics, Supplement}
\newcommand{\azh}             {Astronomicheskii Zhurnal}
\newcommand{\baas}            {Bulletin of the AAS}
\newcommand{\caa}             {Chinese Astronomy and Astrophysics}
\newcommand{\cjaa}            {Chinese Journal of Astronomy and Astrophysics}
\newcommand{\icarus}          {Icarus}
\newcommand{\jcap}            {Journal of Cosmology and Astroparticle Physics}
\newcommand{\jrasc}           {Journal of the RAS of Canada}
\newcommand{\memras}          {Memoirs of the RAS}
\newcommand{\mnras}           {Monthly Notices of the RAS}
\newcommand{\na}              {New Astronomy}
\newcommand{\nar}             {New Astronomy Review}
\newcommand{\pra}             {Physical Review A: General Physics}
\newcommand{\prb}             {Physical Review B: Solid State}
\newcommand{\prc}             {Physical Review C}
\newcommand{\prd}             {Physical Review D}
\newcommand{\pre}             {Physical Review E}
\newcommand{\prl}             {Physical Review Letters}
\newcommand{\pasa}            {Publications of the Astron. Soc. of Australia}
\newcommand{\pasp}            {Publications of the ASP}
\newcommand{\pasj}            {Publications of the ASJ}
\newcommand{\rmxaa}           {Revista Mexicana de Astronomia y Astrofisica}
\newcommand{\qjras}           {Quarterly Journal of the RAS}
\newcommand{\skytel}          {Sky and Telescope}
\newcommand{\solphys}         {Solar Physics}
\newcommand{\sovast}          {Soviet Astronomy}
\newcommand{\ssr}             {Space Science Reviews}
\newcommand{\zap}             {Zeitschrift fuer Astrophysik}
\newcommand{\nat}             {Nature}
\newcommand{\iaucirc}         {IAU Circulars}
\newcommand{\aplett}          {Astrophysics Letters}
\newcommand{\apspr}           {Astrophysics Space Physics Research}
\newcommand{\bain}            {Bulletin Astronomical Institute of the Netherlands}
\newcommand{\fcp}             {Fundamental Cosmic Physics}
\newcommand{\gca}             {Geochimica Cosmochimica Acta}
\newcommand{\grl}             {Geophysics Research Letters}
\newcommand{\jcp}             {Journal of Chemical Physics}
\newcommand{\jgr}             {Journal of Geophysics Research}
\newcommand{\jqsrt}           {Journal of Quantitiative Spectroscopy and Radiative Transfer}
\newcommand{\memsai}          {Mem. Societa Astronomica Italiana}
\newcommand{\nphysa}          {Nuclear Physics A}
\newcommand{\physrep}         {Physics Reports}
\newcommand{\physscr}         {Physica Scripta}
\newcommand{\planss}          {Planetary Space Science}
\newcommand{\procspie}        {Proceedings of the SPIE}

% toto je pouzite pri zrkadlovo obratenom vysledku
\def\mirror{\special{!userdict begin /bop-hook {-1 1 scale -595 0 translate} bind def end}}

\AtBeginDocument%
{\@ifpackageloaded{natbib}{%
      %\def\newblock{\par}
      \def\newblock{\hskip .11em \@plus.33em \@minus.07em}%
      \setlength{\bibsep}{4pt plus 0.3ex} 
}{}
}%AtBeginDocument
%
\endinput
%%
%% End of file `caosp310.cls'.
