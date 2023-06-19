// https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/

export enum ADFBlockNodeType {
  doc = 'doc',
  blockquote = 'blockquote',
  bulletList = 'bulletList',
  codeBlock = 'codeBlock',
  heading = 'heading',
  mediaGroup = 'mediaGroup',
  mediaSingle = 'mediaSingle',
  orderedList = 'orderedList',
  panel = 'panel',
  paragraph = 'paragraph',
  rule = 'rule',
  table = 'table',
}

export enum ADFChildBlockNodeType {
  listItem = 'listItem',
  media = 'media',
  table_cell = 'table_cell',
  table_header = 'table_header',
  table_row = 'table_row',
}

export enum ADFInlineNodeType {
  emoji = 'emoji',
  hardBreak = 'hardBreak',
  inlineCard = 'inlineCard',
  mention = 'mention',
  text = 'text',
}

export enum ADFMarkType {
  code = 'code',
  em = 'em',
  link = 'link',
  strike = 'strike',
  strong = 'strong',
  subsup = 'subsup',
  textColor = 'textColor',
  underline = 'underline',
}

export interface ADFMark {
  type: ADFMarkType;
  attrs?: unknown;
}

export interface ADFNode {
  type: ADFBlockNodeType | ADFChildBlockNodeType | ADFInlineNodeType;
  marks?: ADFMark[];
  attrs?: unknown;
}

export interface ADFBlockNode extends ADFNode {
  type: ADFBlockNodeType | ADFChildBlockNodeType;
  content: ADFNode[];
}

export interface ADFInlineNode extends ADFNode {
  type: ADFInlineNodeType;
}

export interface ADFRootNode extends ADFBlockNode {
  type: ADFBlockNodeType.doc;
  version: number;
}

/* https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/paragraph/ */
export interface ADFParagraphNode extends ADFBlockNode {
  type: ADFBlockNodeType.paragraph;
}

/* https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/listItem/ */
export interface ADFListItemNode extends ADFBlockNode {
  type: ADFChildBlockNodeType.listItem;
}

/* https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/bulletList/ */
export interface ADFBulletListNode extends ADFBlockNode {
  type: ADFBlockNodeType.bulletList;
  content: ADFListItemNode[];
}

/* https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/mention/ */
export interface ADFMentionNode extends ADFInlineNode {
  type: ADFInlineNodeType.mention;
  attrs: {
    accessLevel?: 'NONE' | 'SITE' | 'APPLICATION' | 'CONTAINER';
    id: string;
    text?: string;
    userType?: 'DEFAULT' | 'SPECIAL' | 'APP';
  };
}

/* https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/text/ */
export interface ADFTextNode extends ADFInlineNode {
  // TODO: Not all Marks can be used on all Nodes. We should limit the possible marks to only the available types on each node.
  type: ADFInlineNodeType.text;
  text: string; // cannot be empty string
}

export interface ADFLinkMark extends ADFMark {
  type: ADFMarkType.link,
  attrs: {
    collection?: string;
    href: string;
    id?: string;
    occurrenceKey?: string;
    title?: string;
  }
}

// LinkAttrs: https://developer.atlassian.com/cloud/jira/platform/apis/document/marks/link/#attributes

// This object definition is incomplete
// https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/
