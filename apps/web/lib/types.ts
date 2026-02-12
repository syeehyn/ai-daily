export type Paper = {
  id: string;
  title: string;
  authors: string;
  summary: string;
  tags: string[];
  url: string;
  markdown: string;
  image?: string;
};

export type Issue = {
  date: string;
  title: string;
  digest?: string;
  papers: Paper[];
};
