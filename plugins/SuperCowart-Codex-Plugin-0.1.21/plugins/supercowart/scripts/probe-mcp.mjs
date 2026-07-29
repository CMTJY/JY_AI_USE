import { mkdir, mkdtemp, readFile, rm, unlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const PROBE_SCHEMA = {
  schemaVersion: 2,
  sequences: {
    "com.tldraw.store": 5,
    "com.tldraw.asset": 1,
    "com.tldraw.camera": 1,
    "com.tldraw.document": 2,
    "com.tldraw.instance": 26,
    "com.tldraw.instance_page_state": 5,
    "com.tldraw.page": 1,
    "com.tldraw.instance_presence": 6,
    "com.tldraw.pointer": 1,
    "com.tldraw.shape": 4,
    "com.tldraw.user": 1,
    "com.tldraw.asset.image": 6,
    "com.tldraw.asset.video": 5,
    "com.tldraw.asset.bookmark": 2,
    "com.tldraw.shape.arrow": 8,
    "com.tldraw.shape.bookmark": 2,
    "com.tldraw.shape.draw": 4,
    "com.tldraw.shape.embed": 4,
    "com.tldraw.shape.frame": 1,
    "com.tldraw.shape.geo": 11,
    "com.tldraw.shape.group": 0,
    "com.tldraw.shape.highlight": 3,
    "com.tldraw.shape.image": 5,
    "com.tldraw.shape.line": 5,
    "com.tldraw.shape.note": 12,
    "com.tldraw.shape.text": 4,
    "com.tldraw.shape.video": 4,
    "com.tldraw.binding.arrow": 1,
  },
};

const transport = new StdioClientTransport({
  command: "node",
  args: ["./scripts/start-mcp.mjs"],
});

const client = new Client({
  name: "cowart-probe",
  version: "0.1.0",
});

await client.connect(transport);

let downloadedProbePath = null;
let downloadedProbeDirectory = null;

function isCanvasDirectory(value) {
  const canvasDir = String(value || "");
  return (
    path.basename(path.normalize(canvasDir)) === "canvas" ||
    path.win32.basename(path.win32.normalize(canvasDir)) === "canvas"
  );
}

try {
  const tools = await client.listTools();
  const toolNames = tools.tools.map((tool) => tool.name);
  const requiredTools = [
    "render_cowart_canvas_widget",
    "get_cowart_canvas_state",
    "save_cowart_canvas_state",
    "save_cowart_selection_state",
    "save_cowart_view_state",
    "save_cowart_reference_image",
    "read_cowart_page_asset",
    "download_cowart_file",
    "get_cowart_selection",
    "edit_cowart_canvas",
    "insert_cowart_image",
    "insert_cowart_html_draft",
  ];

  for (const toolName of requiredTools) {
    if (!toolNames.includes(toolName)) {
      throw new Error(`${toolName} not found. Tools: ${toolNames.join(", ")}`);
    }
  }

  const projectDir = await mkdtemp(path.join(tmpdir(), "cowart-widget-probe-"));
  const renderResult = await client.callTool({
    name: "render_cowart_canvas_widget",
    arguments: {
      projectDir,
      title: "Probe SuperCowart",
    },
  });
  if (renderResult._meta?.["openai/outputTemplate"] !== "ui://widget/cowart/canvas.html") {
    throw new Error("SuperCowart render tool result did not include the expected outputTemplate.");
  }
  if (renderResult.structuredContent?.preferredDisplayMode !== "fullscreen") {
    throw new Error("SuperCowart render tool did not default to fullscreen display mode.");
  }
  if (renderResult.structuredContent?.projectDir !== projectDir) {
    throw new Error("SuperCowart render tool did not preserve the requested projectDir.");
  }

  const stateResult = await client.callTool({
    name: "get_cowart_canvas_state",
    arguments: {
      projectDir,
    },
  });
  if (stateResult.structuredContent?.storage !== "empty") {
    throw new Error("A fresh SuperCowart project should report empty storage.");
  }
  if (!isCanvasDirectory(stateResult.structuredContent?.canvasDir)) {
    throw new Error("SuperCowart canvas state did not report a project-local canvas directory.");
  }
  if ((stateResult.structuredContent?.hydratedAssets || []).length !== 0) {
    throw new Error("SuperCowart canvas state should not hydrate image assets by default.");
  }

  const pageId = "page:probe";
  const initialSnapshot = {
    schema: PROBE_SCHEMA,
    store: {
      "document:document": {
        gridSize: 10,
        name: "",
        meta: {},
        id: "document:document",
        typeName: "document",
      },
      [pageId]: {
        meta: {},
        id: pageId,
        name: "Probe Page",
        index: "a1",
        typeName: "page",
      },
    },
  };
  const initialSaveResult = await client.callTool({
    name: "save_cowart_canvas_state",
    arguments: {
      projectDir,
      snapshot: initialSnapshot,
    },
  });
  if (initialSaveResult.isError || initialSaveResult.structuredContent?.ok !== true) {
    throw new Error("SuperCowart probe could not create its initial canvas snapshot.");
  }

  const canvasEditResult = await client.callTool({
    name: "edit_cowart_canvas",
    arguments: {
      projectDir,
      pageId,
      operations: [
        {
          op: "create",
          kind: "rectangle",
          clientId: "start",
          x: 40,
          y: 60,
          w: 180,
          h: 90,
          text: "Start",
          fill: "semi",
          color: "blue",
        },
        {
          op: "create",
          kind: "diamond",
          clientId: "decision",
          x: 320,
          y: 45,
          w: 160,
          h: 120,
          text: "Ready?",
          fill: "semi",
          color: "orange",
        },
        {
          op: "connect",
          clientId: "flow",
          fromShapeId: "$start",
          toShapeId: "$decision",
          text: "next",
          color: "grey",
        },
        {
          op: "create",
          kind: "ai_slides",
          clientId: "deck",
          x: 40,
          y: 240,
        },
      ],
    },
  });
  if (canvasEditResult.isError || canvasEditResult.structuredContent?.createdShapeIds?.length !== 4) {
    throw new Error("SuperCowart native canvas edit tool did not create the expected flowchart and Slides shapes.");
  }
  const slidesShapeId = canvasEditResult.structuredContent?.aliases?.deck;
  if (!slidesShapeId) throw new Error("SuperCowart canvas edit tool did not resolve the AI Slides clientId alias.");

  const editedStateResult = await client.callTool({
    name: "get_cowart_canvas_state",
    arguments: {
      projectDir,
    },
  });
  const editedStore = editedStateResult.structuredContent?.snapshot?.store || {};
  if (
    editedStore[slidesShapeId]?.meta?.cowartAiSlides !== true ||
    editedStore[slidesShapeId]?.props?.w !== 1048 ||
    editedStore[slidesShapeId]?.props?.h !== 600
  ) {
    throw new Error("SuperCowart native canvas edit tool did not create a valid AI Slides frame.");
  }

  const slideInsertResult = await client.callTool({
    name: "insert_cowart_html_draft",
    arguments: {
      projectDir,
      pageId,
      draftShapeId: slidesShapeId,
      replaceDraftHolder: false,
      updateExistingDraft: false,
      matchAnchor: false,
      displayWidth: 1024,
      displayHeight: 576,
      fileName: "probe-slide.html",
      htmlContent: "<!doctype html><html><body>probe slide</body></html>",
    },
  });
  if (slideInsertResult.isError || slideInsertResult.structuredContent?.parentId !== slidesShapeId) {
    throw new Error("SuperCowart HTML draft tool could not append a page to an AI-created Slides frame.");
  }

  const probePageAssetDir = path.join(projectDir, "canvas", "pages", "probe-page", "assets");
  await mkdir(probePageAssetDir, { recursive: true });
  await writeFile(
    path.join(probePageAssetDir, "tiny.png"),
    Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=", "base64"),
  );
  await writeFile(path.join(probePageAssetDir, "draft.html"), "<!doctype html><html><body>draft</body></html>");
  const pageAssetResult = await client.callTool({
    name: "read_cowart_page_asset",
    arguments: {
      projectDir,
      assetUrl: "/page-assets/probe-page/tiny.png",
    },
  });
  if (pageAssetResult.structuredContent?.mimeType !== "image/png" || !pageAssetResult.structuredContent?.dataBase64) {
    throw new Error("SuperCowart page asset tool did not return the expected png payload.");
  }
  const htmlAssetResult = await client.callTool({
    name: "read_cowart_page_asset",
    arguments: {
      projectDir,
      assetUrl: "/page-assets/probe-page/draft.html",
    },
  });
  if (htmlAssetResult.structuredContent?.mimeType !== "text/html" || !htmlAssetResult.structuredContent?.dataBase64) {
    throw new Error("SuperCowart page asset tool did not return the expected html payload.");
  }

  const downloadResult = await client.callTool({
    name: "download_cowart_file",
    arguments: {
      projectDir,
      assetUrl: "/page-assets/probe-page/tiny.png",
      fileName: `cowart-download-probe-${process.pid}.png`,
    },
  });
  downloadedProbePath = downloadResult.structuredContent?.filePath;
  if (!downloadedProbePath || !(await readFile(downloadedProbePath)).length) {
    throw new Error("SuperCowart download tool did not write the expected file into Downloads.");
  }

  const folderDownloadResult = await client.callTool({
    name: "download_cowart_file",
    arguments: {
      projectDir,
      dataUrl: "data:text/html;charset=utf-8,%3C!doctype%20html%3E%3Ctitle%3Eprobe%3C%2Ftitle%3E",
      directoryName: `SuperCowart Slides Probe ${process.pid}`,
      subdirectory: "pages",
      fileName: "page-01.html",
      mimeType: "text/html",
      overwrite: true,
      uniqueDirectory: true,
    },
  });
  downloadedProbeDirectory = folderDownloadResult.structuredContent?.directoryPath;
  const folderDownloadPath = folderDownloadResult.structuredContent?.filePath;
  if (
    !downloadedProbeDirectory ||
    path.basename(path.dirname(folderDownloadPath || "")) !== "pages" ||
    !(await readFile(folderDownloadPath, "utf8")).includes("<title>probe</title>")
  ) {
    throw new Error("SuperCowart download tool did not create the expected Slides export folder structure.");
  }

  const resource = await client.readResource({
    uri: "ui://widget/cowart/canvas.html",
  });
  const resourceMeta = resource.contents?.[0]?._meta || {};
  const widgetCsp = resourceMeta["openai/widgetCSP"] || {};
  const resourceDomains = widgetCsp.resource_domains || [];
  if (!resourceDomains.includes("data:") || !resourceDomains.includes("blob:")) {
    throw new Error(`SuperCowart widget CSP should allow local data/blob resources. Found: ${resourceDomains.join(", ")}`);
  }
  const frameDomains = widgetCsp.frame_domains || [];
  if (!frameDomains.includes("data:") || !frameDomains.includes("blob:")) {
    throw new Error(`SuperCowart widget CSP should allow local data/blob iframes for HTML drafts. Found: ${frameDomains.join(", ")}`);
  }

  const widgetHtml = resource.contents?.[0]?.text || "";
  if (!widgetHtml.includes("window.cowartMcp") || !widgetHtml.includes("SuperCowart Canvas")) {
    throw new Error("SuperCowart widget HTML does not include the expected bridge and app shell.");
  }
  if (/<script\b[^>]*\btype="module"/i.test(widgetHtml)) {
    throw new Error("SuperCowart widget HTML should use classic inline scripts for host compatibility.");
  }
  const shellMarkup = widgetHtml
    .replace(/<script\b[\s\S]*?<\/script>/gi, "")
    .replace(/<style\b[\s\S]*?<\/style>/gi, "");
  if (/<iframe\b/i.test(shellMarkup) || /<script\b[^>]+\bsrc=/i.test(shellMarkup) || /<link\b[^>]+\bhref=/i.test(shellMarkup)) {
    throw new Error("SuperCowart widget HTML should be direct static markup without iframe or external asset tags.");
  }

  console.log("OK: SuperCowart MCP tools and native widget resource are available.");
} finally {
  if (downloadedProbePath) {
    await unlink(downloadedProbePath).catch(() => undefined);
  }
  if (downloadedProbeDirectory) {
    await rm(downloadedProbeDirectory, { recursive: true, force: true }).catch(() => undefined);
  }
  await client.close();
}
