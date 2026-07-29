import { readFileSync } from "node:fs";
import { copyFile, mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { basename, extname, join, relative, resolve, sep } from "node:path";

import { registerAppTool } from "@modelcontextprotocol/ext-apps/server";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { generateKeyBetween } from "fractional-indexing";
import { z } from "zod";

import { sanitizeCanvasSnapshotForTldraw } from "../src/canvasSnapshot.js";
import {
  COWART_STATIC_BUILD_DIR,
  cowartStaticHtml,
} from "./lib/cowart-static-widget.mjs";
import {
  nonEmptyString,
  pageAssetUrl,
  pageDirName,
  pathResolve,
  readSuperCowartCanvasState,
  readSuperCowartPageAsset,
  readSuperCowartSelectionState,
  readSuperCowartViewState,
  resolveCanvasDir,
  resolveSuperCowartPaths,
  saveSuperCowartCanvasSnapshot,
  writeSuperCowartPageAsset,
  writeSuperCowartSelectionState,
  writeSuperCowartViewState,
} from "./lib/canvas-storage.mjs";
import { pluginPath } from "./lib/plugin-root.mjs";
import { inlineWidget, registerWidgetResource } from "./lib/widget-resource.mjs";

const TOOL_RENDER_WIDGET = "render_cowart_canvas_widget";
const TOOL_GET_CANVAS_STATE = "get_cowart_canvas_state";
const TOOL_SAVE_CANVAS_STATE = "save_cowart_canvas_state";
const TOOL_SAVE_SELECTION_STATE = "save_cowart_selection_state";
const TOOL_SAVE_VIEW_STATE = "save_cowart_view_state";
const TOOL_GET_SELECTION = "get_cowart_selection";
const TOOL_EDIT_CANVAS = "edit_cowart_canvas";
const TOOL_INSERT_IMAGE = "insert_cowart_image";
const TOOL_INSERT_HTML_DRAFT = "insert_cowart_html_draft";
const TOOL_SAVE_REFERENCE_IMAGE = "save_cowart_reference_image";
const TOOL_READ_PAGE_ASSET = "read_cowart_page_asset";
const TOOL_DOWNLOAD_FILE = "download_cowart_file";

const PAGE_ID_PREFIX = "page:";
const COWART_WIDGET_URI = "ui://widget/cowart/canvas.html";
const COWART_HTML_DRAFT_URL_ORIGIN = "http://cowart.local";
const DEFAULT_DISPLAY_MODE = "fullscreen";
const COWART_RESOURCE_DOMAINS = ["data:", "blob:"];
const COWART_FRAME_DOMAINS = ["data:", "blob:"];

const projectArgsSchema = {
  projectDir: z.string().trim().optional(),
  canvasDir: z.string().trim().optional(),
};

const displayModeSchema = z.enum(["fullscreen", "inline"]);
const tldrawColorSchema = z.enum([
  "black",
  "grey",
  "light-violet",
  "violet",
  "blue",
  "light-blue",
  "yellow",
  "orange",
  "green",
  "light-green",
  "light-red",
  "red",
  "white",
]);
const tldrawFillSchema = z.enum(["none", "semi", "solid", "pattern"]);
const tldrawDashSchema = z.enum(["draw", "solid", "dashed", "dotted"]);
const tldrawSizeSchema = z.enum(["s", "m", "l", "xl"]);
const tldrawFontSchema = z.enum(["draw", "sans", "serif", "mono"]);
const tldrawAlignSchema = z.enum(["start", "middle", "end"]);
const canvasShapeKindSchema = z.enum([
  "rectangle",
  "ellipse",
  "diamond",
  "text",
  "frame",
  "ai_slides",
]);
const canvasPointSchema = z.object({
  x: z.number(),
  y: z.number(),
});
const canvasCreateOperationSchema = z.object({
  op: z.literal("create"),
  kind: canvasShapeKindSchema,
  clientId: z.string().trim().optional(),
  shapeId: z.string().trim().optional(),
  parentId: z.string().trim().optional(),
  x: z.number().optional(),
  y: z.number().optional(),
  w: z.number().positive().optional(),
  h: z.number().positive().optional(),
  rotation: z.number().optional(),
  text: z.string().optional(),
  name: z.string().optional(),
  color: tldrawColorSchema.optional(),
  labelColor: tldrawColorSchema.optional(),
  fill: tldrawFillSchema.optional(),
  dash: tldrawDashSchema.optional(),
  size: tldrawSizeSchema.optional(),
  font: tldrawFontSchema.optional(),
  align: tldrawAlignSchema.optional(),
  verticalAlign: tldrawAlignSchema.optional(),
  autoSize: z.boolean().optional(),
  locked: z.boolean().optional(),
  opacity: z.number().min(0).max(1).optional(),
  meta: z.record(z.string(), z.unknown()).optional(),
});
const canvasConnectOperationSchema = z.object({
  op: z.literal("connect"),
  clientId: z.string().trim().optional(),
  shapeId: z.string().trim().optional(),
  parentId: z.string().trim().optional(),
  fromShapeId: z.string().trim().optional(),
  toShapeId: z.string().trim().optional(),
  start: canvasPointSchema.optional(),
  end: canvasPointSchema.optional(),
  text: z.string().optional(),
  color: tldrawColorSchema.optional(),
  labelColor: tldrawColorSchema.optional(),
  dash: tldrawDashSchema.optional(),
  size: tldrawSizeSchema.optional(),
  arrowheadStart: z.enum(["none", "arrow", "triangle", "square", "dot", "diamond", "inverted", "bar"]).optional(),
  arrowheadEnd: z.enum(["none", "arrow", "triangle", "square", "dot", "diamond", "inverted", "bar"]).optional(),
  bend: z.number().optional(),
  meta: z.record(z.string(), z.unknown()).optional(),
});
const canvasUpdateOperationSchema = z.object({
  op: z.literal("update"),
  shapeId: z.string().trim(),
  parentId: z.string().trim().optional(),
  x: z.number().optional(),
  y: z.number().optional(),
  w: z.number().positive().optional(),
  h: z.number().positive().optional(),
  rotation: z.number().optional(),
  text: z.string().optional(),
  name: z.string().optional(),
  color: tldrawColorSchema.optional(),
  labelColor: tldrawColorSchema.optional(),
  fill: tldrawFillSchema.optional(),
  dash: tldrawDashSchema.optional(),
  size: tldrawSizeSchema.optional(),
  font: tldrawFontSchema.optional(),
  align: tldrawAlignSchema.optional(),
  verticalAlign: tldrawAlignSchema.optional(),
  autoSize: z.boolean().optional(),
  locked: z.boolean().optional(),
  opacity: z.number().min(0).max(1).optional(),
  meta: z.record(z.string(), z.unknown()).optional(),
  replaceMeta: z.boolean().optional(),
});
const canvasDeleteOperationSchema = z.object({
  op: z.literal("delete"),
  shapeId: z.string().trim(),
  cascade: z.boolean().optional(),
  confirmImageDeletion: z.boolean().optional(),
});
const canvasOperationSchema = z.discriminatedUnion("op", [
  canvasCreateOperationSchema,
  canvasConnectOperationSchema,
  canvasUpdateOperationSchema,
  canvasDeleteOperationSchema,
]);

const pluginManifest = JSON.parse(
  readFileSync(pluginPath(".codex-plugin", "plugin.json"), "utf8"),
);

const server = new McpServer(
  {
    name: pluginManifest.name,
    version: pluginManifest.version,
  },
  {
    instructions:
      "Render and update the native SuperCowart Codex widget. Use render_cowart_canvas_widget to open the canvas, edit_cowart_canvas to create or modify native shapes, flowchart connectors, frames, and AI Slides containers, get_cowart_selection for persisted selection, save_cowart_reference_image and read_cowart_page_asset for page-local assets, insert_cowart_image for bitmap assets, and insert_cowart_html_draft for runnable HTML pages.",
  },
);

registerSuperCowartWidget(server);
registerSuperCowartStateTools(server);
registerSuperCowartCanvasEditingTools(server);
registerSuperCowartImageTools(server);

const transport = new StdioServerTransport();
await server.connect(transport);

function finiteNumber(value, fallback) {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function isSafeChildPath(parent, child) {
  const pathToChild = relative(parent, child);
  return pathToChild && !pathToChild.startsWith("..") && !pathToChild.includes(`..${sep}`);
}

function sanitizeFileName(name, fallbackName = "image.png") {
  const rawName = basename(String(name || fallbackName));
  const extension = extname(rawName) || extname(fallbackName) || ".png";
  const baseName = rawName
    .slice(0, rawName.length - extname(rawName).length)
    .replace(/[^a-zA-Z0-9._-]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return `${baseName || "image"}${extension}`;
}

function sanitizeDirectoryName(name, fallbackName = "SuperCowart Export") {
  return basename(String(name || fallbackName))
    .replace(/[<>:"/\\|?*\u0000-\u001f]+/g, "-")
    .replace(/[. ]+$/g, "")
    .trim()
    .slice(0, 120) || fallbackName;
}

function sanitizeHtmlFileName(name, fallbackName = "draft.html") {
  const safeName = sanitizeFileName(name, fallbackName);
  return /\.html?$/i.test(safeName) ? safeName : `${safeName.replace(/\.[^.]+$/, "")}.html`;
}

function sanitizeIdPart(value, fallback = "image") {
  return String(value || fallback)
    .replace(/\.[^.]+$/, "")
    .replace(/[^a-zA-Z0-9_-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80) || fallback;
}

function mimeTypeForFile(filePath) {
  switch (extname(filePath).toLowerCase()) {
    case ".apng":
      return "image/apng";
    case ".avif":
      return "image/avif";
    case ".gif":
      return "image/gif";
    case ".jpg":
    case ".jpeg":
      return "image/jpeg";
    case ".png":
      return "image/png";
    case ".webp":
      return "image/webp";
    case ".svg":
      return "image/svg+xml";
    case ".htm":
    case ".html":
      return "text/html";
    default:
      return "application/octet-stream";
  }
}

function parseDownloadDataUrl(dataUrl) {
  const match = /^data:([^;,]+)?((?:;[^,]*)?),(.*)$/s.exec(String(dataUrl || ""));
  if (!match) throw new Error("Invalid download dataUrl.");
  const mimeType = nonEmptyString(match[1]) || "application/octet-stream";
  const parameters = match[2] || "";
  const payload = match[3] || "";
  const buffer = /;base64(?:;|$)/i.test(parameters)
    ? Buffer.from(payload, "base64")
    : Buffer.from(decodeURIComponent(payload), "utf8");
  return { buffer, mimeType };
}

async function uniqueFilePath(dir, requestedName) {
  const safeName = sanitizeFileName(requestedName);
  const ext = extname(safeName);
  const base = safeName.slice(0, safeName.length - ext.length);
  let candidate = safeName;
  let counter = 2;
  while (true) {
    const candidatePath = join(dir, candidate);
    try {
      await stat(candidatePath);
      candidate = `${base}-v${counter}${ext}`;
      counter += 1;
    } catch (error) {
      if (error?.code === "ENOENT") return { fileName: candidate, filePath: candidatePath };
      throw error;
    }
  }
}

async function uniqueDirectoryPath(dir, requestedName) {
  const safeName = sanitizeDirectoryName(requestedName);
  let candidate = safeName;
  let counter = 2;
  while (true) {
    const candidatePath = join(dir, candidate);
    try {
      await stat(candidatePath);
      candidate = `${safeName}-${counter}`;
      counter += 1;
    } catch (error) {
      if (error?.code === "ENOENT") {
        return { directoryName: candidate, directoryPath: candidatePath };
      }
      throw error;
    }
  }
}

function uniqueRecordId(store, prefix, seed) {
  const cleanSeed = sanitizeIdPart(seed);
  let candidate = `${prefix}:${cleanSeed}`;
  let counter = 2;
  while (store[candidate]) {
    candidate = `${prefix}:${cleanSeed}-${counter}`;
    counter += 1;
  }
  return candidate;
}

function getRecord(store, id, label) {
  const record = store[id];
  if (!record) throw new Error(`Missing ${label}: ${id}`);
  return record;
}

function findPageIdForShape(store, shapeId) {
  let record = getRecord(store, shapeId, "shape");
  const visited = new Set();
  while (record && !visited.has(record.id)) {
    visited.add(record.id);
    if (record.typeName === "page") return record.id;
    const parentId = record.parentId;
    if (!parentId) break;
    const parent = store[parentId];
    if (parent?.typeName === "page") return parent.id;
    record = parent;
  }
  return null;
}

function getPageShapes(store, pageId) {
  const shapes = [];
  const byParent = new Map();
  for (const record of Object.values(store)) {
    if (record?.typeName !== "shape") continue;
    const siblings = byParent.get(record.parentId) ?? [];
    siblings.push(record);
    byParent.set(record.parentId, siblings);
  }
  const queue = [...(byParent.get(pageId) ?? [])];
  while (queue.length > 0) {
    const shape = queue.shift();
    shapes.push(shape);
    queue.push(...(byParent.get(shape.id) ?? []));
  }
  return shapes;
}

function localBoundsForShape(shape) {
  if (!shape || shape.typeName !== "shape") return null;
  if (shape.type === "arrow") {
    const start = shape.props?.start ?? { x: 0, y: 0 };
    const end = shape.props?.end ?? { x: 0, y: 0 };
    const minX = Math.min(start.x ?? 0, end.x ?? 0);
    const minY = Math.min(start.y ?? 0, end.y ?? 0);
    const maxX = Math.max(start.x ?? 0, end.x ?? 0);
    const maxY = Math.max(start.y ?? 0, end.y ?? 0);
    return { x: minX, y: minY, w: Math.max(1, maxX - minX), h: Math.max(1, maxY - minY) };
  }
  const w = finiteNumber(shape.props?.w, shape.type === "text" ? 160 : 1);
  const h = finiteNumber(shape.props?.h, shape.type === "text" ? 40 : 1);
  return { x: 0, y: 0, w, h };
}

function pageBoundsForShape(store, shape) {
  const local = localBoundsForShape(shape);
  if (!local) return null;
  let x = finiteNumber(shape.x, 0) + local.x;
  let y = finiteNumber(shape.y, 0) + local.y;
  let parent = store[shape.parentId];
  const visited = new Set([shape.id]);
  while (parent?.typeName === "shape" && !visited.has(parent.id)) {
    visited.add(parent.id);
    x += finiteNumber(parent.x, 0);
    y += finiteNumber(parent.y, 0);
    parent = store[parent.parentId];
  }
  return { x, y, w: local.w, h: local.h };
}

function rectsOverlap(a, b, padding = 0) {
  return !(
    a.x + a.w + padding <= b.x ||
    b.x + b.w + padding <= a.x ||
    a.y + a.h + padding <= b.y ||
    b.y + b.h + padding <= a.y
  );
}

function chooseIndex(store, parentId) {
  const siblingIndexes = Object.values(store)
    .filter((record) => record?.typeName === "shape" && record.parentId === parentId && typeof record.index === "string")
    .map((record) => record.index)
    .sort();
  return generateKeyBetween(siblingIndexes.at(-1) ?? null, null);
}

function firstSelectedShapeId(selection) {
  return selection?.selectedShapes?.length === 1 ? selection.selectedShapes[0]?.id : null;
}

function isAiImageHolderShape(shape) {
  return shape?.typeName === "shape" && shape.meta?.cowartAiImageHolder === true;
}

function isAiDraftHolderShape(shape) {
  return shape?.typeName === "shape" && shape.meta?.cowartAiDraftHolder === true;
}

function isAiSlidesShape(shape) {
  return shape?.typeName === "shape" && shape.meta?.cowartAiSlides === true;
}

function isSuperCowartHtmlDraftShape(shape) {
  return shape?.typeName === "shape" && shape.type === "embed" && (
    shape.meta?.cowartHtmlDraft === true ||
    /^data:text\/html(?:;[^,]*)?,/i.test(String(shape.props?.url || ""))
  );
}

function cowartHtmlDraftVirtualUrl(assetUrl) {
  return `${COWART_HTML_DRAFT_URL_ORIGIN}${assetUrl}`;
}

function cowartHtmlDraftDataUrl(htmlContent) {
  return `data:text/html;base64,${Buffer.from(String(htmlContent || ""), "utf8").toString("base64")}`;
}

function collectDescendantShapeIds(store, shapeId) {
  if (!shapeId) return [];
  const byParent = new Map();
  for (const record of Object.values(store)) {
    if (record?.typeName !== "shape") continue;
    const children = byParent.get(record.parentId) ?? [];
    children.push(record.id);
    byParent.set(record.parentId, children);
  }

  const descendants = [];
  const queue = [...(byParent.get(shapeId) ?? [])];
  const visited = new Set([shapeId]);
  while (queue.length > 0) {
    const childId = queue.shift();
    if (!childId || visited.has(childId)) continue;
    visited.add(childId);
    descendants.push(childId);
    queue.push(...(byParent.get(childId) ?? []));
  }
  return descendants;
}

function choosePlacement({ store, pageId, parentId, anchorShape, width, height, margin, placement }) {
  const anchorBounds = anchorShape ? pageBoundsForShape(store, anchorShape) : null;
  let x = anchorBounds ? anchorBounds.x + anchorBounds.w + margin : 0;
  let y = anchorBounds ? anchorBounds.y : 0;

  if (placement === "left" && anchorBounds) x = anchorBounds.x - width - margin;
  if (placement === "below" && anchorBounds) {
    x = anchorBounds.x;
    y = anchorBounds.y + anchorBounds.h + margin;
  }

  const pageShapes = getPageShapes(store, pageId);
  const obstacles = pageShapes
    .filter((shape) => shape.parentId === parentId && shape.id !== anchorShape?.id)
    .map((shape) => pageBoundsForShape(store, shape))
    .filter(Boolean);

  const stepX = Math.max(width + margin, 1);
  const stepY = Math.max(height + margin, 1);
  for (let attempt = 0; attempt < 60; attempt += 1) {
    const candidate = { x, y, w: width, h: height };
    if (!obstacles.some((bounds) => rectsOverlap(candidate, bounds, margin / 2))) return candidate;
    if (placement === "below") y += stepY;
    else if (placement === "left") x -= stepX;
    else x += stepX;
  }

  return { x, y, w: width, h: height };
}

function richTextDocument(text = "") {
  const lines = String(text).split(/\r?\n/);
  return {
    type: "doc",
    attrs: { dir: "auto" },
    content: lines.map((line) => ({
      type: "paragraph",
      attrs: { dir: "auto" },
      ...(line ? { content: [{ type: "text", text: line }] } : {}),
    })),
  };
}

function resolveCanvasRecordId(value, aliases) {
  const rawValue = nonEmptyString(value);
  if (!rawValue) return null;
  const alias = rawValue.startsWith("$") ? rawValue.slice(1) : rawValue;
  return aliases.get(alias) || rawValue;
}

function requestedShapeId(store, requestedId, seed) {
  const explicitId = nonEmptyString(requestedId);
  if (!explicitId) return uniqueRecordId(store, "shape", seed);
  if (!explicitId.startsWith("shape:")) {
    throw new Error(`SuperCowart shape ids must start with "shape:". Received: ${explicitId}`);
  }
  if (store[explicitId]) throw new Error(`SuperCowart shape already exists: ${explicitId}`);
  return explicitId;
}

function ensureShapeParent(store, parentId, pageId) {
  const parent = store[parentId];
  if (!parent) throw new Error(`Missing SuperCowart parent: ${parentId}`);
  if (parent.typeName !== "page" && parent.typeName !== "shape") {
    throw new Error(`SuperCowart parent must be a page or shape: ${parentId}`);
  }
  if (parent.typeName === "shape" && findPageIdForShape(store, parent.id) !== pageId) {
    throw new Error(`SuperCowart parent ${parentId} is not on target page ${pageId}.`);
  }
}

function parentPageOrigin(store, parentId) {
  const parent = store[parentId];
  if (!parent || parent.typeName === "page") return { x: 0, y: 0 };
  const bounds = pageBoundsForShape(store, parent);
  return bounds ? { x: bounds.x, y: bounds.y } : { x: 0, y: 0 };
}

function shapeCenterOnPage(store, shapeId) {
  const shape = getRecord(store, shapeId, "connector endpoint shape");
  if (shape.typeName !== "shape") throw new Error(`Connector endpoint is not a shape: ${shapeId}`);
  const bounds = pageBoundsForShape(store, shape);
  if (!bounds) throw new Error(`Could not determine bounds for connector endpoint: ${shapeId}`);
  return {
    x: bounds.x + bounds.w / 2,
    y: bounds.y + bounds.h / 2,
  };
}

function createCanvasShapeRecord({ store, pageId, parentId, shapeId, operation, bounds }) {
  const commonRecord = {
    x: bounds.x,
    y: bounds.y,
    rotation: finiteNumber(operation.rotation, 0),
    isLocked: operation.locked === true,
    opacity: finiteNumber(operation.opacity, 1),
    meta: operation.meta && typeof operation.meta === "object" ? { ...operation.meta } : {},
    id: shapeId,
    parentId,
    index: chooseIndex(store, parentId),
    typeName: "shape",
  };

  if (operation.kind === "ai_slides") {
    return {
      ...commonRecord,
      type: "frame",
      meta: {
        cowartAiSlides: true,
        cowartAiSlidesVersion: 1,
        cowartAiSlidesFlow: "horizontal",
        cowartAiSlidesGap: 32,
        cowartAiSlidesPadding: 12,
        ...commonRecord.meta,
      },
      props: {
        w: bounds.w,
        h: bounds.h,
        name: nonEmptyString(operation.name) || "AI Slides",
        color: operation.color || "blue",
      },
    };
  }

  if (operation.kind === "frame") {
    return {
      ...commonRecord,
      type: "frame",
      props: {
        w: bounds.w,
        h: bounds.h,
        name: nonEmptyString(operation.name) || "Frame",
        color: operation.color || "blue",
      },
    };
  }

  if (operation.kind === "text") {
    return {
      ...commonRecord,
      type: "text",
      props: {
        color: operation.color || "black",
        size: operation.size || "m",
        w: bounds.w,
        font: operation.font || "sans",
        textAlign: operation.align || "start",
        autoSize: operation.autoSize !== false,
        scale: 1,
        richText: richTextDocument(operation.text || ""),
      },
    };
  }

  const geo = operation.kind === "ellipse"
    ? "ellipse"
    : operation.kind === "diamond"
      ? "diamond"
      : "rectangle";
  return {
    ...commonRecord,
    type: "geo",
    props: {
      w: bounds.w,
      h: bounds.h,
      geo,
      dash: operation.dash || "solid",
      growY: 0,
      url: "",
      scale: 1,
      color: operation.color || "black",
      labelColor: operation.labelColor || operation.color || "black",
      fill: operation.fill || "semi",
      size: operation.size || "m",
      font: operation.font || "sans",
      align: operation.align || "middle",
      verticalAlign: operation.verticalAlign || "middle",
      richText: richTextDocument(operation.text || ""),
    },
  };
}

function updateCanvasShapeRecord(store, operation, aliases, pageId) {
  const shapeId = resolveCanvasRecordId(operation.shapeId, aliases);
  const shape = getRecord(store, shapeId, "shape to update");
  if (shape.typeName !== "shape") throw new Error(`SuperCowart update target is not a shape: ${shapeId}`);
  if (findPageIdForShape(store, shapeId) !== pageId) {
    throw new Error(`SuperCowart update target ${shapeId} is not on target page ${pageId}.`);
  }

  const nextShape = {
    ...shape,
    props: shape.props && typeof shape.props === "object" ? { ...shape.props } : {},
  };
  if (operation.x !== undefined) nextShape.x = operation.x;
  if (operation.y !== undefined) nextShape.y = operation.y;
  if (operation.rotation !== undefined) nextShape.rotation = operation.rotation;
  if (operation.locked !== undefined) nextShape.isLocked = operation.locked;
  if (operation.opacity !== undefined) nextShape.opacity = operation.opacity;

  if (operation.parentId !== undefined) {
    const parentId = resolveCanvasRecordId(operation.parentId, aliases);
    ensureShapeParent(store, parentId, pageId);
    if (parentId !== shape.parentId) {
      nextShape.parentId = parentId;
      nextShape.index = chooseIndex(store, parentId);
    }
  }

  if (operation.w !== undefined && "w" in nextShape.props) nextShape.props.w = operation.w;
  if (operation.h !== undefined && "h" in nextShape.props) nextShape.props.h = operation.h;
  if (operation.color !== undefined && "color" in nextShape.props) nextShape.props.color = operation.color;
  if (operation.labelColor !== undefined && "labelColor" in nextShape.props) nextShape.props.labelColor = operation.labelColor;
  if (operation.fill !== undefined && "fill" in nextShape.props) nextShape.props.fill = operation.fill;
  if (operation.dash !== undefined && "dash" in nextShape.props) nextShape.props.dash = operation.dash;
  if (operation.size !== undefined && "size" in nextShape.props) nextShape.props.size = operation.size;
  if (operation.font !== undefined && "font" in nextShape.props) nextShape.props.font = operation.font;
  if (operation.autoSize !== undefined && "autoSize" in nextShape.props) nextShape.props.autoSize = operation.autoSize;
  if (operation.align !== undefined) {
    if ("align" in nextShape.props) nextShape.props.align = operation.align;
    if ("textAlign" in nextShape.props) nextShape.props.textAlign = operation.align;
  }
  if (operation.verticalAlign !== undefined && "verticalAlign" in nextShape.props) {
    nextShape.props.verticalAlign = operation.verticalAlign;
  }
  if (operation.name !== undefined && "name" in nextShape.props) nextShape.props.name = operation.name;
  if (operation.text !== undefined && "richText" in nextShape.props) {
    nextShape.props.richText = richTextDocument(operation.text);
  }

  if (operation.meta !== undefined) {
    nextShape.meta = operation.replaceMeta === true
      ? { ...operation.meta }
      : {
          ...(shape.meta && typeof shape.meta === "object" ? shape.meta : {}),
          ...operation.meta,
        };
  }

  store[shapeId] = nextShape;
  return shapeId;
}

function deleteCanvasShapeRecords(store, operation, aliases, pageId) {
  const shapeId = resolveCanvasRecordId(operation.shapeId, aliases);
  const shape = getRecord(store, shapeId, "shape to delete");
  if (shape.typeName !== "shape") throw new Error(`SuperCowart delete target is not a shape: ${shapeId}`);
  if (findPageIdForShape(store, shapeId) !== pageId) {
    throw new Error(`SuperCowart delete target ${shapeId} is not on target page ${pageId}.`);
  }

  const descendants = collectDescendantShapeIds(store, shapeId);
  if (descendants.length > 0 && operation.cascade === false) {
    throw new Error(`SuperCowart shape ${shapeId} has ${descendants.length} descendant shape(s); set cascade to true to delete them.`);
  }
  const deletedIds = [shapeId, ...descendants];
  const deletedIdSet = new Set(deletedIds);
  const imageShapeIds = deletedIds.filter((id) => store[id]?.typeName === "shape" && store[id]?.type === "image");
  if (imageShapeIds.length > 0 && operation.confirmImageDeletion !== true) {
    throw new Error(`Deleting ${shapeId} would remove ${imageShapeIds.length} image shape(s); set confirmImageDeletion to true.`);
  }

  for (const record of Object.values(store)) {
    if (record?.typeName !== "binding") continue;
    const fromId = record.fromId ?? record.props?.fromId;
    const toId = record.toId ?? record.props?.toId;
    if (deletedIdSet.has(fromId) || deletedIdSet.has(toId)) delete store[record.id];
  }
  for (const id of deletedIds) delete store[id];
  return { deletedIds, imageShapeIds };
}

async function editSuperCowartCanvas(args = {}) {
  const canvasState = await readSuperCowartCanvasState(args, { hydrateAssets: false });
  const sourceSnapshot = canvasState.snapshot;
  if (!sourceSnapshot || typeof sourceSnapshot !== "object" || !sourceSnapshot.schema || !sourceSnapshot.store) {
    throw new Error("No SuperCowart canvas snapshot exists yet. Open the SuperCowart widget for the target project before editing native shapes.");
  }

  const snapshot = structuredClone(sourceSnapshot);
  const store = snapshot.store;
  const { selection } = await readSuperCowartSelectionState(args);
  const { viewState } = await readSuperCowartViewState(args);
  const anchorShapeId = nonEmptyString(args.anchorShapeId) || firstSelectedShapeId(selection);
  const anchorShape = anchorShapeId ? getRecord(store, anchorShapeId, "anchor shape") : null;
  const pageId =
    nonEmptyString(args.pageId) ||
    (anchorShape ? findPageIdForShape(store, anchorShape.id) : null) ||
    nonEmptyString(viewState?.currentPageId) ||
    Object.values(store).find((record) => record?.typeName === "page")?.id;
  if (!pageId || store[pageId]?.typeName !== "page") throw new Error("Could not determine target SuperCowart pageId.");

  const operations = Array.isArray(args.operations) ? args.operations : [];
  if (operations.length === 0) throw new Error("At least one SuperCowart canvas operation is required.");

  const aliases = new Map();
  const createdIds = [];
  const updatedIds = [];
  const deletedIds = [];
  const acknowledgedImageShapeDeletes = new Set();
  const margin = Math.max(0, finiteNumber(args.margin, 40));
  const placement = ["right", "left", "below"].includes(args.placement) ? args.placement : "right";
  let placementAnchor = anchorShape;

  for (const [operationIndex, operation] of operations.entries()) {
    if (operation.op === "create") {
      const clientId = nonEmptyString(operation.clientId);
      if (clientId && aliases.has(clientId)) throw new Error(`Duplicate SuperCowart clientId: ${clientId}`);
      const shapeId = requestedShapeId(
        store,
        operation.shapeId,
        clientId || `${operation.kind}-${Date.now()}-${operationIndex + 1}`,
      );
      const parentId = resolveCanvasRecordId(operation.parentId, aliases) || pageId;
      ensureShapeParent(store, parentId, pageId);
      const defaultWidth = operation.kind === "ai_slides"
        ? 1048
        : operation.kind === "text"
          ? 240
          : operation.kind === "frame"
            ? 640
            : 200;
      const defaultHeight = operation.kind === "ai_slides"
        ? 600
        : operation.kind === "text"
          ? 48
          : operation.kind === "frame"
            ? 360
            : 120;
      const width = finiteNumber(operation.w, defaultWidth);
      const height = finiteNumber(operation.h, defaultHeight);
      let x = operation.x;
      let y = operation.y;
      if (x === undefined || y === undefined) {
        if (parentId === pageId) {
          const planned = choosePlacement({
            store,
            pageId,
            parentId,
            anchorShape: placementAnchor,
            width,
            height,
            margin,
            placement,
          });
          x ??= planned.x;
          y ??= planned.y;
        } else {
          x ??= 12;
          y ??= 12;
        }
      }
      const record = createCanvasShapeRecord({
        store,
        pageId,
        parentId,
        shapeId,
        operation,
        bounds: { x, y, w: width, h: height },
      });
      store[shapeId] = record;
      createdIds.push(shapeId);
      placementAnchor = record;
      if (clientId) aliases.set(clientId, shapeId);
      continue;
    }

    if (operation.op === "connect") {
      const clientId = nonEmptyString(operation.clientId);
      if (clientId && aliases.has(clientId)) throw new Error(`Duplicate SuperCowart clientId: ${clientId}`);
      const fromShapeId = resolveCanvasRecordId(operation.fromShapeId, aliases);
      const toShapeId = resolveCanvasRecordId(operation.toShapeId, aliases);
      const startPoint = fromShapeId ? shapeCenterOnPage(store, fromShapeId) : operation.start;
      const endPoint = toShapeId ? shapeCenterOnPage(store, toShapeId) : operation.end;
      if (!startPoint || !endPoint) {
        throw new Error("SuperCowart connect operations require fromShapeId/toShapeId or explicit start/end points.");
      }
      if (fromShapeId && findPageIdForShape(store, fromShapeId) !== pageId) {
        throw new Error(`Connector source ${fromShapeId} is not on target page ${pageId}.`);
      }
      if (toShapeId && findPageIdForShape(store, toShapeId) !== pageId) {
        throw new Error(`Connector target ${toShapeId} is not on target page ${pageId}.`);
      }
      const parentId = resolveCanvasRecordId(operation.parentId, aliases) || pageId;
      ensureShapeParent(store, parentId, pageId);
      const origin = parentPageOrigin(store, parentId);
      const localStart = { x: startPoint.x - origin.x, y: startPoint.y - origin.y };
      const shapeId = requestedShapeId(
        store,
        operation.shapeId,
        clientId || `connector-${Date.now()}-${operationIndex + 1}`,
      );
      store[shapeId] = {
        x: localStart.x,
        y: localStart.y,
        rotation: 0,
        isLocked: false,
        opacity: 1,
        meta: {
          ...(operation.meta && typeof operation.meta === "object" ? operation.meta : {}),
          ...(fromShapeId ? { cowartConnectorFromShapeId: fromShapeId } : {}),
          ...(toShapeId ? { cowartConnectorToShapeId: toShapeId } : {}),
        },
        id: shapeId,
        type: "arrow",
        props: {
          kind: "arc",
          elbowMidPoint: 0.5,
          dash: operation.dash || "solid",
          size: operation.size || "m",
          fill: "none",
          color: operation.color || "black",
          labelColor: operation.labelColor || operation.color || "black",
          bend: finiteNumber(operation.bend, 0),
          start: { x: 0, y: 0 },
          end: { x: endPoint.x - startPoint.x, y: endPoint.y - startPoint.y },
          arrowheadStart: operation.arrowheadStart || "none",
          arrowheadEnd: operation.arrowheadEnd || "arrow",
          richText: richTextDocument(operation.text || ""),
          labelPosition: 0.5,
          font: "sans",
          scale: 1,
        },
        parentId,
        index: chooseIndex(store, parentId),
        typeName: "shape",
      };
      createdIds.push(shapeId);
      if (clientId) aliases.set(clientId, shapeId);
      continue;
    }

    if (operation.op === "update") {
      updatedIds.push(updateCanvasShapeRecord(store, operation, aliases, pageId));
      continue;
    }

    if (operation.op === "delete") {
      const deletion = deleteCanvasShapeRecords(store, operation, aliases, pageId);
      deletedIds.push(...deletion.deletedIds);
      for (const id of deletion.imageShapeIds) acknowledgedImageShapeDeletes.add(id);
    }
  }

  const validation = sanitizeCanvasSnapshotForTldraw(snapshot);
  if (!validation.snapshot) throw new Error("SuperCowart canvas edit produced an invalid tldraw snapshot.");
  if (validation.skippedRecords.length > 0) {
    const details = validation.skippedRecords
      .slice(0, 5)
      .map((record) => `${record.id}: ${record.reason}`)
      .join("; ");
    throw new Error(`SuperCowart canvas edit validation failed without saving: ${details}`);
  }
  for (const shapeId of createdIds) {
    if (!validation.snapshot.store[shapeId]) {
      throw new Error(`SuperCowart canvas edit validation removed created shape ${shapeId}; nothing was saved.`);
    }
  }

  let saveResult = null;
  if (!args.dryRun) {
    saveResult = await saveSuperCowartCanvasSnapshot(
      {
        ...args,
        acknowledgedImageShapeDeletes: Array.from(acknowledgedImageShapeDeletes),
      },
      validation.snapshot,
    );
    if (!saveResult.ok) throw new Error(saveResult.message || "SuperCowart canvas edit could not be saved.");
  }

  return {
    ok: true,
    canvasDir: resolveCanvasDir(args),
    pageId,
    aliases: Object.fromEntries(aliases),
    createdShapeIds: createdIds,
    updatedShapeIds: Array.from(new Set(updatedIds)),
    deletedShapeIds: Array.from(new Set(deletedIds)),
    operationCount: operations.length,
    dryRun: Boolean(args.dryRun),
    storage: saveResult?.storage || canvasState.storage,
  };
}

async function getImageDimensions(filePath) {
  const buffer = await readFile(filePath);
  if (buffer.length >= 24 && buffer.toString("ascii", 1, 4) === "PNG") {
    return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
  }
  if (buffer.length >= 10 && buffer[0] === 0xff && buffer[1] === 0xd8) {
    let offset = 2;
    while (offset < buffer.length) {
      if (buffer[offset] !== 0xff) break;
      const marker = buffer[offset + 1];
      const size = buffer.readUInt16BE(offset + 2);
      if ((marker >= 0xc0 && marker <= 0xc3) || (marker >= 0xc5 && marker <= 0xc7) || (marker >= 0xc9 && marker <= 0xcb) || (marker >= 0xcd && marker <= 0xcf)) {
        return { width: buffer.readUInt16BE(offset + 7), height: buffer.readUInt16BE(offset + 5) };
      }
      offset += 2 + size;
    }
  }
  if (buffer.length >= 30 && buffer.toString("ascii", 0, 4) === "RIFF" && buffer.toString("ascii", 8, 12) === "WEBP") {
    const chunk = buffer.toString("ascii", 12, 16);
    if (chunk === "VP8X") {
      return {
        width: 1 + buffer.readUIntLE(24, 3),
        height: 1 + buffer.readUIntLE(27, 3),
      };
    }
  }
  throw new Error(`Could not read image dimensions for ${filePath}. Pass displayWidth/displayHeight and use a PNG/JPEG/WebP source.`);
}

async function insertSuperCowartImage(args = {}) {
  const imagePath = nonEmptyString(args.imagePath);
  if (!imagePath) throw new Error("imagePath is required.");

  const sourceImagePath = pathResolve(imagePath);
  const sourceStat = await stat(sourceImagePath);
  if (!sourceStat.isFile()) throw new Error(`imagePath is not a file: ${sourceImagePath}`);

  const canvasState = await readSuperCowartCanvasState(args, { hydrateAssets: false });
  const snapshot = canvasState.snapshot;
  if (!snapshot || typeof snapshot !== "object" || !snapshot.schema || !snapshot.store) {
    throw new Error("No SuperCowart canvas snapshot exists yet. Open the SuperCowart widget for the target project and create or save the canvas before inserting images.");
  }

  const store = snapshot.store;
  const { selection } = await readSuperCowartSelectionState(args);
  const { viewState } = await readSuperCowartViewState(args);

  const anchorShapeId = nonEmptyString(args.anchorShapeId) || nonEmptyString(args.sourceShapeId) || firstSelectedShapeId(selection);
  const anchorShape = anchorShapeId ? getRecord(store, anchorShapeId, "anchor shape") : null;
  const pageId =
    nonEmptyString(args.pageId) ||
    (anchorShape ? findPageIdForShape(store, anchorShape.id) : null) ||
    nonEmptyString(viewState?.currentPageId) ||
    Object.values(store).find((record) => record?.typeName === "page")?.id;
  if (!pageId || !store[pageId]) throw new Error("Could not determine target pageId.");

  const imageSize = await getImageDimensions(sourceImagePath);
  const anchorBounds = anchorShape ? pageBoundsForShape(store, anchorShape) : null;
  const shouldTargetAiImageHolder = args.matchAnchor !== false && isAiImageHolderShape(anchorShape) && anchorBounds;
  const shouldReplaceAiImageHolder = shouldTargetAiImageHolder && args.replaceAiImageHolder !== false;
  const shouldFillAiImageHolder = shouldTargetAiImageHolder && !shouldReplaceAiImageHolder;
  const matchAnchor = args.matchAnchor !== false && anchorBounds;
  const width = shouldTargetAiImageHolder
    ? anchorBounds.w
    : finiteNumber(args.displayWidth, matchAnchor ? anchorBounds.w : Math.min(imageSize.width, 512));
  const height = shouldTargetAiImageHolder
    ? anchorBounds.h
    : finiteNumber(
      args.displayHeight,
      matchAnchor ? anchorBounds.h : Math.round(width * (imageSize.height / imageSize.width)),
    );
  const margin = Math.max(0, finiteNumber(args.margin, 40));
  const placement = ["right", "left", "below"].includes(args.placement) ? args.placement : "right";
  let parentId = anchorShape?.parentId && store[anchorShape.parentId] ? anchorShape.parentId : pageId;
  let rotation = 0;
  let bounds = null;

  if (shouldFillAiImageHolder && anchorShape.type === "frame") {
    parentId = anchorShape.id;
    bounds = { x: 0, y: 0, w: width, h: height };
  } else if (shouldTargetAiImageHolder) {
    parentId = anchorShape.parentId && store[anchorShape.parentId] ? anchorShape.parentId : pageId;
    rotation = finiteNumber(anchorShape.rotation, 0);
    bounds = {
      x: finiteNumber(anchorShape.x, 0),
      y: finiteNumber(anchorShape.y, 0),
      w: width,
      h: height,
    };
  } else {
    parentId = anchorShape?.parentId && store[anchorShape.parentId]?.typeName === "page" ? anchorShape.parentId : pageId;
    bounds = choosePlacement({ store, pageId, parentId, anchorShape, width, height, margin, placement });
  }

  const canvasDir = resolveCanvasDir(args);
  const assetsDir = join(canvasDir, "pages", pageDirName(pageId), "assets");
  if (!isSafeChildPath(resolveCanvasDir(args), assetsDir)) {
    throw new Error(`Unsafe page assets directory: ${assetsDir}`);
  }
  const { fileName, filePath } = await uniqueFilePath(assetsDir, args.fileName || basename(sourceImagePath));
  const recordSeed = sanitizeIdPart(fileName);
  const assetId = uniqueRecordId(store, "asset", recordSeed);
  const shapeId = uniqueRecordId(store, "shape", recordSeed);
  const replacedShapeIds = shouldReplaceAiImageHolder && anchorShapeId
    ? [anchorShapeId, ...collectDescendantShapeIds(store, anchorShapeId)]
    : [];
  const replacedImageShapeIds = replacedShapeIds.filter((id) => store[id]?.typeName === "shape" && store[id]?.type === "image");
  const index = shouldReplaceAiImageHolder && typeof anchorShape?.index === "string"
    ? anchorShape.index
    : chooseIndex(store, parentId);
  const mimeType = mimeTypeForFile(fileName);

  const assetRecord = {
    id: assetId,
    typeName: "asset",
    type: "image",
    props: {
      name: fileName,
      src: pageAssetUrl(pageId, fileName),
      w: imageSize.width,
      h: imageSize.height,
      fileSize: sourceStat.size,
      mimeType,
      isAnimated: false,
    },
    meta: args.assetMeta && typeof args.assetMeta === "object" ? args.assetMeta : {},
  };

  const shapeMeta = args.shapeMeta && typeof args.shapeMeta === "object" ? { ...args.shapeMeta } : {};
  if (anchorShapeId && !shapeMeta.cowartAnnotationSourceShapeId) {
    shapeMeta.cowartAnnotationSourceShapeId = anchorShapeId;
  }
  if (shouldTargetAiImageHolder && anchorShapeId && !shapeMeta.cowartGeneratedForAiImageHolder) {
    shapeMeta.cowartGeneratedForAiImageHolder = anchorShapeId;
  }
  if (shouldReplaceAiImageHolder && anchorShapeId) {
    shapeMeta.cowartReplacedAiImageHolder = true;
  }
  if (nonEmptyString(args.annotationScreenshot) && !shapeMeta.cowartAnnotationScreenshot) {
    shapeMeta.cowartAnnotationScreenshot = nonEmptyString(args.annotationScreenshot);
  }

  const shapeRecord = {
    x: bounds.x,
    y: bounds.y,
    rotation,
    isLocked: false,
    opacity: 1,
    meta: shapeMeta,
    id: shapeId,
    type: "image",
    props: {
      w: width,
      h: height,
      assetId,
      playing: true,
      url: "",
      crop: null,
      flipX: false,
      flipY: false,
      altText: nonEmptyString(args.altText) || "SuperCowart inserted image",
    },
    parentId,
    index,
    typeName: "shape",
  };

  if (!args.dryRun) {
    await mkdir(assetsDir, { recursive: true });
    await copyFile(sourceImagePath, filePath);
    for (const replacedShapeId of replacedShapeIds) {
      delete store[replacedShapeId];
    }
    store[assetId] = assetRecord;
    store[shapeId] = shapeRecord;
    const saveArgs = replacedImageShapeIds.length > 0
      ? {
          ...args,
          acknowledgedImageShapeDeletes: Array.from(new Set([
            ...(Array.isArray(args.acknowledgedImageShapeDeletes) ? args.acknowledgedImageShapeDeletes : []),
            ...replacedImageShapeIds,
          ])),
        }
      : args;
    await saveSuperCowartCanvasSnapshot(saveArgs, snapshot);
  }

  return {
    canvasDir,
    cowartUrl: nonEmptyString(args.cowartUrl),
    pageId,
    parentId,
    anchorShapeId,
    assetId,
    shapeId,
    index,
    sourceImagePath,
    assetFile: filePath,
    assetUrl: assetRecord.props.src,
    imageSize,
    bounds,
    replacedAiImageHolder: shouldReplaceAiImageHolder,
    replacedShapeIds,
    dryRun: Boolean(args.dryRun),
  };
}

async function insertSuperCowartHtmlDraft(args = {}) {
  const htmlContent = nonEmptyString(args.htmlContent);
  const htmlPath = nonEmptyString(args.htmlPath);
  if (!htmlContent && !htmlPath) {
    throw new Error("htmlContent or htmlPath is required.");
  }

  const sourceHtmlPath = htmlPath ? pathResolve(htmlPath) : null;
  const finalHtml = htmlContent ?? await readFile(sourceHtmlPath, "utf8");
  if (!nonEmptyString(finalHtml)) {
    throw new Error("HTML draft content is empty.");
  }
  if (sourceHtmlPath) {
    const sourceStat = await stat(sourceHtmlPath);
    if (!sourceStat.isFile()) throw new Error(`htmlPath is not a file: ${sourceHtmlPath}`);
  }

  const canvasState = await readSuperCowartCanvasState(args, { hydrateAssets: false });
  const snapshot = canvasState.snapshot;
  if (!snapshot || typeof snapshot !== "object" || !snapshot.schema || !snapshot.store) {
    throw new Error("No SuperCowart canvas snapshot exists yet. Open the SuperCowart widget for the target project and create or save the canvas before inserting HTML drafts.");
  }

  const store = snapshot.store;
  const { selection } = await readSuperCowartSelectionState(args);
  const { viewState } = await readSuperCowartViewState(args);

  const draftShapeId = nonEmptyString(args.draftShapeId) || nonEmptyString(args.anchorShapeId) || firstSelectedShapeId(selection);
  const draftShape = draftShapeId ? getRecord(store, draftShapeId, "AI draft holder shape") : null;
  const pageId =
    nonEmptyString(args.pageId) ||
    (draftShape ? findPageIdForShape(store, draftShape.id) : null) ||
    nonEmptyString(viewState?.currentPageId) ||
    Object.values(store).find((record) => record?.typeName === "page")?.id;
  if (!pageId || !store[pageId]) throw new Error("Could not determine target pageId.");

  const anchorBounds = draftShape ? pageBoundsForShape(store, draftShape) : null;
  const shouldUpdateExistingDraft = args.updateExistingDraft !== false && isSuperCowartHtmlDraftShape(draftShape) && anchorBounds;
  const shouldTargetDraftHolder = args.matchAnchor !== false && isAiDraftHolderShape(draftShape) && anchorBounds;
  const shouldTargetAiSlides = isAiSlidesShape(draftShape);
  const shouldReplaceDraftHolder = shouldTargetDraftHolder && args.replaceDraftHolder !== false;
  const matchAnchor = args.matchAnchor !== false && anchorBounds;
  const width = shouldUpdateExistingDraft || shouldTargetDraftHolder
    ? anchorBounds.w
    : finiteNumber(args.displayWidth, shouldTargetAiSlides ? 1024 : matchAnchor ? anchorBounds.w : 512);
  const height = shouldUpdateExistingDraft || shouldTargetDraftHolder
    ? anchorBounds.h
    : finiteNumber(args.displayHeight, shouldTargetAiSlides ? 576 : matchAnchor ? anchorBounds.h : 683);
  const margin = Math.max(0, finiteNumber(args.margin, 40));
  const placement = ["right", "left", "below"].includes(args.placement) ? args.placement : "right";
  let parentId = draftShape?.parentId && store[draftShape.parentId] ? draftShape.parentId : pageId;
  let rotation = 0;
  let bounds = null;

  if (shouldTargetAiSlides) {
    const padding = Math.max(0, finiteNumber(draftShape.meta?.cowartAiSlidesPadding, 12));
    const gap = Math.max(0, finiteNumber(draftShape.meta?.cowartAiSlidesGap, 32));
    const slideItems = Object.values(store)
      .filter((record) => record?.typeName === "shape" && record.parentId === draftShape.id)
      .sort((a, b) => String(a.index || "").localeCompare(String(b.index || "")));
    const nextX = slideItems.reduce(
      (cursor, item) => Math.max(cursor, finiteNumber(item.x, padding) + finiteNumber(item.props?.w, 0) + gap),
      padding,
    );
    parentId = draftShape.id;
    rotation = 0;
    bounds = { x: nextX, y: padding, w: width, h: height };
  } else if (shouldUpdateExistingDraft || shouldTargetDraftHolder) {
    parentId = draftShape.parentId && store[draftShape.parentId] ? draftShape.parentId : pageId;
    rotation = finiteNumber(draftShape.rotation, 0);
    bounds = {
      x: finiteNumber(draftShape.x, 0),
      y: finiteNumber(draftShape.y, 0),
      w: width,
      h: height,
    };
  } else {
    parentId = draftShape?.parentId && store[draftShape.parentId]?.typeName === "page" ? draftShape.parentId : pageId;
    bounds = choosePlacement({ store, pageId, parentId, anchorShape: draftShape, width, height, margin, placement });
  }

  const canvasDir = resolveCanvasDir(args);
  const assetsDir = join(canvasDir, "pages", pageDirName(pageId), "assets");
  if (!isSafeChildPath(canvasDir, assetsDir)) {
    throw new Error(`Unsafe page assets directory: ${assetsDir}`);
  }
  const existingAssetUrl = shouldUpdateExistingDraft
    ? nonEmptyString(draftShape.meta?.cowartHtmlDraftAssetUrl)
    : null;
  const expectedAssetPrefix = `/page-assets/${pageDirName(pageId)}/`;
  let existingFileName = null;
  if (existingAssetUrl?.startsWith(expectedAssetPrefix)) {
    try {
      existingFileName = decodeURIComponent(existingAssetUrl.slice(expectedAssetPrefix.length).split(/[?#]/)[0]);
    } catch (_error) {
      existingFileName = null;
    }
  }
  const shouldForkSharedAsset = Boolean(
    shouldUpdateExistingDraft &&
      existingAssetUrl &&
      Object.values(store).some(
        (record) =>
          record?.id !== draftShape.id &&
          isSuperCowartHtmlDraftShape(record) &&
          nonEmptyString(record.meta?.cowartHtmlDraftAssetUrl) === existingAssetUrl,
      ),
  );
  const requestedName = sanitizeHtmlFileName(
    existingFileName || args.fileName,
    `draft-${Date.now()}.html`,
  );
  const fileTarget = shouldUpdateExistingDraft && existingFileName && !shouldForkSharedAsset
    ? { fileName: requestedName, filePath: join(assetsDir, requestedName) }
    : await uniqueFilePath(assetsDir, requestedName);
  const { fileName, filePath } = fileTarget;
  if (!isSafeChildPath(assetsDir, filePath)) {
    throw new Error(`Unsafe HTML draft file path: ${filePath}`);
  }
  const recordSeed = sanitizeIdPart(fileName, "html-draft");
  const shapeId = shouldUpdateExistingDraft ? draftShape.id : uniqueRecordId(store, "shape", recordSeed);
  const replacedShapeIds = shouldReplaceDraftHolder && draftShapeId
    ? [draftShapeId, ...collectDescendantShapeIds(store, draftShapeId)]
    : [];
  const index = shouldUpdateExistingDraft && typeof draftShape?.index === "string"
    ? draftShape.index
    : shouldReplaceDraftHolder && typeof draftShape?.index === "string"
    ? draftShape.index
    : chooseIndex(store, parentId);
  const assetUrl = pageAssetUrl(pageId, fileName);
  const shapeMeta = args.shapeMeta && typeof args.shapeMeta === "object" ? { ...args.shapeMeta } : {};
  if (shouldTargetDraftHolder && draftShapeId && !shapeMeta.cowartGeneratedForAiDraftHolder) {
    shapeMeta.cowartGeneratedForAiDraftHolder = draftShapeId;
  }
  if (shouldReplaceDraftHolder && draftShapeId) {
    shapeMeta.cowartReplacedAiDraftHolder = true;
  }
  if (shouldTargetAiSlides && draftShapeId && !shapeMeta.cowartAiSlidesParentShapeId) {
    shapeMeta.cowartAiSlidesParentShapeId = draftShapeId;
  }

  const shapeRecord = {
    x: bounds.x,
    y: bounds.y,
    rotation,
    isLocked: false,
    opacity: 1,
    meta: {
      ...(shouldUpdateExistingDraft && draftShape.meta && typeof draftShape.meta === "object" ? draftShape.meta : {}),
      cowartHtmlDraft: true,
      cowartHtmlDraftAssetUrl: assetUrl,
      ...shapeMeta,
    },
    id: shapeId,
    type: "embed",
    props: {
      ...(shouldUpdateExistingDraft && draftShape.props && typeof draftShape.props === "object" ? draftShape.props : {}),
      w: width,
      h: height,
      url: cowartHtmlDraftDataUrl(finalHtml),
    },
    parentId,
    index,
    typeName: "shape",
  };

  if (!args.dryRun) {
    await mkdir(assetsDir, { recursive: true });
    await writeFile(filePath, finalHtml);
    for (const replacedShapeId of replacedShapeIds) {
      delete store[replacedShapeId];
    }
    store[shapeId] = shapeRecord;
    await saveSuperCowartCanvasSnapshot(args, snapshot);
  }

  return {
    canvasDir,
    pageId,
    parentId,
    draftShapeId,
    shapeId,
    index,
    assetFile: filePath,
    assetUrl,
    virtualUrl: cowartHtmlDraftVirtualUrl(assetUrl),
    displayUrlKind: "data:text/html;base64",
    bounds,
    updatedExistingHtmlDraft: Boolean(shouldUpdateExistingDraft),
    forkedSharedHtmlDraftAsset: shouldForkSharedAsset,
    replacedAiDraftHolder: shouldReplaceDraftHolder,
    replacedShapeIds,
    dryRun: Boolean(args.dryRun),
  };
}

async function saveSuperCowartReferenceImage(args = {}) {
  const canvasState = await readSuperCowartCanvasState(args, { hydrateAssets: false });
  const snapshot = canvasState.snapshot;
  if (!snapshot || typeof snapshot !== "object" || !snapshot.schema || !snapshot.store) {
    throw new Error("No SuperCowart canvas snapshot exists yet. Open the SuperCowart widget for the target project and create or save the canvas before saving reference images.");
  }

  const store = snapshot.store;
  const { selection } = await readSuperCowartSelectionState(args);
  const { viewState } = await readSuperCowartViewState(args);
  const holderShapeId = nonEmptyString(args.holderShapeId) || nonEmptyString(args.anchorShapeId) || firstSelectedShapeId(selection);
  const holderShape = holderShapeId ? getRecord(store, holderShapeId, "AI image holder shape") : null;
  const pageId =
    nonEmptyString(args.pageId) ||
    (holderShape ? findPageIdForShape(store, holderShape.id) : null) ||
    nonEmptyString(viewState?.currentPageId) ||
    Object.values(store).find((record) => record?.typeName === "page")?.id;
  if (!pageId || !store[pageId]) throw new Error("Could not determine target pageId for the reference image.");

  const result = await writeSuperCowartPageAsset(args, {
    pageId,
    fileName: args.fileName,
    dataUrl: args.dataUrl,
    dataBase64: args.dataBase64,
    mimeType: args.mimeType,
  });
  const { projectDir } = resolveSuperCowartPaths(args);

  return {
    ...result,
    projectDir,
    holderShapeId: holderShape?.id ?? holderShapeId ?? null,
    assetPathRelativeToProject: relative(projectDir, result.assetPath),
    assetPathRelativeToCanvas: relative(result.canvasDir, result.assetPath),
  };
}

async function downloadSuperCowartFile(args = {}) {
  const assetUrl = nonEmptyString(args.assetUrl);
  const dataUrl = nonEmptyString(args.dataUrl);
  const dataBase64 = nonEmptyString(args.dataBase64);
  let buffer = null;
  let mimeType = nonEmptyString(args.mimeType) || "application/octet-stream";
  let sourceFileName = null;

  if (assetUrl) {
    const asset = await readSuperCowartPageAsset(args, { assetUrl });
    buffer = Buffer.from(asset.dataBase64, "base64");
    mimeType = asset.mimeType || mimeType;
    sourceFileName = basename(asset.assetPath);
  } else if (dataUrl) {
    const parsed = parseDownloadDataUrl(dataUrl);
    buffer = parsed.buffer;
    mimeType = nonEmptyString(args.mimeType) || parsed.mimeType;
  } else if (dataBase64) {
    buffer = Buffer.from(dataBase64, "base64");
  } else {
    throw new Error("assetUrl, dataUrl, or dataBase64 is required.");
  }

  if (!buffer.length) throw new Error("SuperCowart download data is empty.");

  const downloadsDir = join(homedir(), "Downloads");
  const requestedName = sanitizeFileName(
    nonEmptyString(args.fileName) || sourceFileName,
    `cowart-download-${Date.now()}.png`,
  );
  const requestedDirectoryName = nonEmptyString(args.directoryName);
  const requestedSubdirectory = nonEmptyString(args.subdirectory);
  let directoryName = requestedDirectoryName
    ? sanitizeDirectoryName(requestedDirectoryName)
    : null;
  let exportRoot = directoryName ? join(downloadsDir, directoryName) : downloadsDir;
  if (directoryName && args.uniqueDirectory === true) {
    const uniqueDirectory = await uniqueDirectoryPath(downloadsDir, directoryName);
    directoryName = uniqueDirectory.directoryName;
    exportRoot = uniqueDirectory.directoryPath;
  }
  const targetDir = requestedSubdirectory
    ? join(exportRoot, sanitizeDirectoryName(requestedSubdirectory, "pages"))
    : exportRoot;
  if (!isSafeChildPath(downloadsDir, targetDir) && targetDir !== downloadsDir) {
    throw new Error("Invalid SuperCowart download directory.");
  }
  await mkdir(targetDir, { recursive: true });
  const { fileName, filePath } = args.overwrite === true
    ? { fileName: requestedName, filePath: join(targetDir, requestedName) }
    : await uniqueFilePath(targetDir, requestedName);
  await writeFile(filePath, buffer);

  return {
    ok: true,
    fileName,
    filePath,
    directoryName,
    directoryPath: exportRoot,
    mimeType,
    fileSize: buffer.length,
  };
}

function registerSuperCowartWidget(mcpServer) {
  registerWidgetResource(mcpServer, {
    name: "supercowart-canvas-widget",
    uri: COWART_WIDGET_URI,
    title: "SuperCowart Canvas",
    description:
      "A native Codex widget that renders SuperCowart's tldraw canvas directly and persists canvas data in the active project.",
    resourceDomains: COWART_RESOURCE_DOMAINS,
    frameDomains: COWART_FRAME_DOMAINS,
    html: async () => inlineWidget({
      html: await cowartStaticHtml(),
      initialDisplayMode: DEFAULT_DISPLAY_MODE,
    }),
  });

  registerAppTool(
    mcpServer,
    TOOL_RENDER_WIDGET,
    {
      title: "Render SuperCowart Canvas Widget",
      description:
        "Open the native SuperCowart canvas widget for the active Codex project. Pass projectDir for the user's workspace so canvas data is stored under <projectDir>/canvas.",
      inputSchema: {
        ...projectArgsSchema,
        title: z.string().trim().optional(),
        displayMode: displayModeSchema.optional(),
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
      _meta: {
        ui: {
          resourceUri: COWART_WIDGET_URI,
          visibility: ["model", "app"],
        },
        "ui/resourceUri": COWART_WIDGET_URI,
        "openai/outputTemplate": COWART_WIDGET_URI,
        "openai/widgetAccessible": true,
        "openai/toolInvocation/invoking": "Opening SuperCowart canvas...",
        "openai/toolInvocation/invoked": "SuperCowart canvas ready",
      },
    },
    async (input = {}) => {
      const { projectDir, canvasDir } = resolveSuperCowartPaths(input);
      const title = nonEmptyString(input.title) || "SuperCowart Canvas";
      const preferredDisplayMode = normalizeDisplayMode(input.displayMode);

      return {
        content: [
          {
            type: "text",
            text: "Rendered SuperCowart canvas widget.",
          },
        ],
        structuredContent: {
          version: 1,
          widget: "supercowart-canvas-widget",
          title,
          rendering: "native-widget",
          staticDir: COWART_STATIC_BUILD_DIR,
          projectDir,
          canvasDir,
          preferredDisplayMode,
        },
        _meta: {
          "openai/outputTemplate": COWART_WIDGET_URI,
          widgetData: {
            title,
            rendering: "native-widget",
            staticDir: COWART_STATIC_BUILD_DIR,
            projectDir,
            canvasDir,
            preferredDisplayMode,
          },
        },
      };
    },
  );
}

function registerSuperCowartStateTools(mcpServer) {
  mcpServer.registerTool(
    TOOL_GET_CANVAS_STATE,
    {
      title: "Get SuperCowart Canvas State",
      description:
        "Read the project-backed SuperCowart canvas snapshot, view state, and storage paths. The widget uses this instead of a localhost /api/canvas request.",
      inputSchema: {
        ...projectArgsSchema,
        hydrateAssets: z.boolean().optional(),
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async (input = {}) => {
      const state = await readSuperCowartCanvasState(input, { hydrateAssets: input.hydrateAssets === true });
      return {
        content: [
          {
            type: "text",
            text: `Loaded SuperCowart canvas state from ${state.canvasDir} (${state.storage}).`,
          },
        ],
        structuredContent: state,
      };
    },
  );

  mcpServer.registerTool(
    TOOL_READ_PAGE_ASSET,
    {
      title: "Read SuperCowart Page Asset",
      description:
        "Read one project-local SuperCowart /page-assets/... image or HTML asset for lazy widget rendering. Prefer this over hydrating all assets into the canvas snapshot.",
      inputSchema: {
        ...projectArgsSchema,
        assetUrl: z.string().trim(),
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async (input = {}) => {
      const asset = await readSuperCowartPageAsset(input, { assetUrl: input.assetUrl });
      return {
        content: [
          {
            type: "text",
            text: `Loaded SuperCowart page asset ${asset.assetUrl}.`,
          },
        ],
        structuredContent: asset,
      };
    },
  );

  mcpServer.registerTool(
    TOOL_SAVE_CANVAS_STATE,
    {
      title: "Save SuperCowart Canvas State",
      description:
        "Persist a SuperCowart/tldraw store snapshot to the project canvas directory, preserving per-page files and page-local assets.",
      inputSchema: {
        ...projectArgsSchema,
        snapshot: z.any(),
        protectImageRecords: z.boolean().optional(),
        acknowledgedImageShapeDeletes: z.array(z.string()).optional(),
      },
      annotations: {
        readOnlyHint: false,
        destructiveHint: false,
        idempotentHint: false,
        openWorldHint: false,
      },
    },
    async (input = {}) => {
      const result = await saveSuperCowartCanvasSnapshot(input, input.snapshot);
      if (!result.ok) {
        return {
          isError: true,
          content: [
            {
              type: "text",
              text: result.message || "Invalid SuperCowart canvas snapshot.",
            },
          ],
          structuredContent: result,
        };
      }
      return {
        content: [
          {
            type: "text",
            text: `Saved SuperCowart canvas state (${result.storage}).`,
          },
        ],
        structuredContent: result,
      };
    },
  );

  mcpServer.registerTool(
    TOOL_SAVE_SELECTION_STATE,
    {
      title: "Save SuperCowart Selection State",
      description:
        "Persist the current SuperCowart widget selection to canvas/cowart-selection.json so Codex can target selected shapes.",
      inputSchema: {
        ...projectArgsSchema,
        selection: z.any(),
      },
      annotations: {
        readOnlyHint: false,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async (input = {}) => {
      const result = await writeSuperCowartSelectionState(input, input.selection);
      return {
        content: [
          {
            type: "text",
            text: `Saved SuperCowart selection state to ${result.path}.`,
          },
        ],
        structuredContent: result,
      };
    },
  );

  mcpServer.registerTool(
    TOOL_SAVE_VIEW_STATE,
    {
      title: "Save SuperCowart View State",
      description:
        "Persist the current SuperCowart page and camera state to canvas/cowart-view-state.json.",
      inputSchema: {
        ...projectArgsSchema,
        viewState: z.any(),
      },
      annotations: {
        readOnlyHint: false,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async (input = {}) => {
      const result = await writeSuperCowartViewState(input, input.viewState);
      return {
        content: [
          {
            type: "text",
            text: `Saved SuperCowart view state to ${result.path}.`,
          },
        ],
        structuredContent: result,
      };
    },
  );
}

function registerSuperCowartCanvasEditingTools(mcpServer) {
  mcpServer.registerTool(
    TOOL_EDIT_CANVAS,
    {
      title: "Edit SuperCowart Canvas",
      description:
        "Create, connect, update, or delete native SuperCowart/tldraw shapes in one atomic batch. Supports rectangles, ellipses, diamonds, text, frames, flowchart arrows, and correctly configured AI Slides frames. Use clientId aliases such as node_a and reference them later as $node_a inside the same call.",
      inputSchema: {
        ...projectArgsSchema,
        pageId: z.string().trim().optional(),
        anchorShapeId: z.string().trim().optional(),
        placement: z.enum(["right", "left", "below"]).optional(),
        margin: z.number().optional(),
        operations: z.array(canvasOperationSchema).min(1).max(200),
        dryRun: z.boolean().optional(),
      },
      annotations: {
        readOnlyHint: false,
        destructiveHint: true,
        idempotentHint: false,
        openWorldHint: false,
      },
    },
    async (input = {}) => {
      const result = await editSuperCowartCanvas(input);
      return {
        content: [
          {
            type: "text",
            text: `${result.dryRun ? "Planned" : "Applied"} ${result.operationCount} SuperCowart canvas operation(s) on ${result.pageId}: ${result.createdShapeIds.length} created, ${result.updatedShapeIds.length} updated, ${result.deletedShapeIds.length} deleted.`,
          },
        ],
        structuredContent: result,
      };
    },
  );
}

function registerSuperCowartImageTools(mcpServer) {
  mcpServer.registerTool(
    TOOL_DOWNLOAD_FILE,
    {
      title: "Download SuperCowart File",
      description:
        "Save an image, HTML draft, or exported Slides package file requested by the SuperCowart widget into the user's system Downloads folder.",
      inputSchema: {
        ...projectArgsSchema,
        assetUrl: z.string().trim().optional(),
        fileName: z.string().trim().optional(),
        dataUrl: z.string().optional(),
        dataBase64: z.string().optional(),
        mimeType: z.string().trim().optional(),
        directoryName: z.string().trim().optional(),
        subdirectory: z.string().trim().optional(),
        overwrite: z.boolean().optional(),
        uniqueDirectory: z.boolean().optional(),
      },
      annotations: {
        readOnlyHint: false,
        destructiveHint: false,
        idempotentHint: false,
        openWorldHint: false,
      },
    },
    async (input = {}) => {
      const result = await downloadSuperCowartFile(input);
      return {
        content: [
          {
            type: "text",
            text: `Downloaded SuperCowart file to ${result.filePath}.`,
          },
        ],
        structuredContent: result,
      };
    },
  );

  mcpServer.registerTool(
    TOOL_SAVE_REFERENCE_IMAGE,
    {
      title: "Save SuperCowart Reference Image",
      description:
        "Save a widget-selected reference image into the current SuperCowart page's assets folder so Codex can read it from the local project when ui/message image attachments are unavailable.",
      inputSchema: {
        ...projectArgsSchema,
        holderShapeId: z.string().trim().optional(),
        anchorShapeId: z.string().trim().optional(),
        pageId: z.string().trim().optional(),
        fileName: z.string().trim().optional(),
        dataUrl: z.string().optional(),
        dataBase64: z.string().optional(),
        mimeType: z.string().trim().optional(),
      },
      annotations: {
        readOnlyHint: false,
        destructiveHint: false,
        idempotentHint: false,
        openWorldHint: false,
      },
    },
    async (input = {}) => {
      const result = await saveSuperCowartReferenceImage(input);
      return {
        content: [
          {
            type: "text",
            text: `Saved SuperCowart reference image to ${result.assetPath}.`,
          },
        ],
        structuredContent: result,
      };
    },
  );

  mcpServer.registerTool(
    TOOL_INSERT_HTML_DRAFT,
    {
      title: "Insert SuperCowart HTML Draft",
      description:
        "Save a single-file HTML draft into the current SuperCowart page's assets folder, update a targeted existing HTML draft in place, replace a targeted AI HTML holder, or append a 16:9 HTML page inside an AI Slides frame.",
      inputSchema: {
        ...projectArgsSchema,
        htmlContent: z.string().optional(),
        htmlPath: z.string().trim().optional(),
        draftShapeId: z.string().trim().optional(),
        anchorShapeId: z.string().trim().optional(),
        pageId: z.string().trim().optional(),
        fileName: z.string().trim().optional(),
        placement: z.enum(["right", "left", "below"]).optional(),
        margin: z.number().optional(),
        matchAnchor: z.boolean().optional(),
        replaceDraftHolder: z.boolean().optional(),
        updateExistingDraft: z.boolean().optional(),
        displayWidth: z.number().optional(),
        displayHeight: z.number().optional(),
        shapeMeta: z.record(z.string(), z.unknown()).optional(),
        dryRun: z.boolean().optional(),
      },
      annotations: {
        readOnlyHint: false,
        destructiveHint: true,
        idempotentHint: false,
        openWorldHint: false,
      },
    },
    async (input = {}) => {
      const result = await insertSuperCowartHtmlDraft(input);
      return {
        content: [
          {
            type: "text",
            text: `${result.dryRun ? "Planned" : "Inserted"} HTML draft ${result.shapeId} on ${result.pageId} at (${result.bounds.x}, ${result.bounds.y}) using ${result.index}.`,
          },
        ],
        structuredContent: result,
      };
    },
  );

  mcpServer.registerTool(
    TOOL_GET_SELECTION,
    {
      title: "Get SuperCowart Selection",
      description:
        "Return the currently selected SuperCowart/tldraw shapes and image asset metadata from a project's canvas/cowart-selection.json state file.",
      inputSchema: projectArgsSchema,
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async (input = {}) => {
      const { selection, selectionFile } = await readSuperCowartSelectionState(input);
      const selectedShapes = selection.selectedShapes ?? [];
      const summary =
        selectedShapes.length === 0
          ? "No SuperCowart shapes are currently selected."
          : selectedShapes
              .map((shape) => {
                const assetName = shape.asset?.name ? ` (${shape.asset.name})` : "";
                return `${shape.id} [${shape.type ?? "unknown"}]${assetName}`;
              })
              .join("\n");

      return {
        content: [{ type: "text", text: summary }],
        structuredContent: { selection, selectionFile },
      };
    },
  );

  mcpServer.registerTool(
    TOOL_INSERT_IMAGE,
    {
      title: "Insert SuperCowart Image",
      description:
        "Copy a local bitmap into a SuperCowart page-local assets folder, create a tldraw image asset and shape, replace a targeted AI image holder by default, otherwise place it beside an anchor or clear page area, and save the project-backed SuperCowart canvas.",
      inputSchema: {
        imagePath: z.string().trim(),
        projectDir: z.string().trim().optional(),
        canvasDir: z.string().trim().optional(),
        cowartUrl: z.string().trim().optional(),
        pageId: z.string().trim().optional(),
        anchorShapeId: z.string().trim().optional(),
        sourceShapeId: z.string().trim().optional(),
        fileName: z.string().trim().optional(),
        placement: z.enum(["right", "left", "below"]).optional(),
        margin: z.number().optional(),
        matchAnchor: z.boolean().optional(),
        replaceAiImageHolder: z.boolean().optional(),
        displayWidth: z.number().optional(),
        displayHeight: z.number().optional(),
        altText: z.string().trim().optional(),
        annotationScreenshot: z.string().trim().optional(),
        shapeMeta: z.record(z.string(), z.unknown()).optional(),
        assetMeta: z.record(z.string(), z.unknown()).optional(),
        dryRun: z.boolean().optional(),
      },
      annotations: {
        readOnlyHint: false,
        destructiveHint: true,
        idempotentHint: false,
        openWorldHint: false,
      },
    },
    async (input = {}) => {
      const result = await insertSuperCowartImage(input);
      return {
        content: [
          {
            type: "text",
            text: `${result.dryRun ? "Planned" : "Inserted"} ${result.shapeId} on ${result.pageId} at (${result.bounds.x}, ${result.bounds.y}) using ${result.index}.`,
          },
        ],
        structuredContent: result,
      };
    },
  );
}

function normalizeDisplayMode(displayMode) {
  const parsed = displayModeSchema.safeParse(displayMode);
  return parsed.success ? parsed.data : DEFAULT_DISPLAY_MODE;
}
