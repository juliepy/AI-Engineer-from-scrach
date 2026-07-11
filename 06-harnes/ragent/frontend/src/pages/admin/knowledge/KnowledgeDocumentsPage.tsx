import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Check, FileUp, Image, PlayCircle, RefreshCw, Trash2, Pencil, FileBarChart, X, Eye, MoreHorizontal, FileText, Link as LinkIcon } from "lucide-react";
import { toast } from "sonner";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";

import { cn } from "@/lib/utils";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { RelativeTime } from "@/components/RelativeTime";
import { formatFullDateTime } from "@/utils/time";

import type { KnowledgeBase, KnowledgeDocument, KnowledgeDocumentUploadPayload, KnowledgeDocumentChunkLog, PageResult, ChunkStrategyOption } from "@/services/knowledgeService";
import {
  deleteDocument,
  enableDocument,
  getKnowledgeBase,
  getDocumentsPage,
  getDocument,
  updateDocument,
  startDocumentChunk,
  uploadDocument,
  getChunkStrategies,
  getChunkLogsPage,
  previewDocument
} from "@/services/knowledgeService";
import { getIngestionPipelines, type IngestionPipeline } from "@/services/ingestionService";
import { getSystemSettings } from "@/services/settingsService";
import { MarkdownRenderer } from "@/components/chat/MarkdownRenderer";
import { getErrorMessage } from "@/utils/error";

const PAGE_SIZE = 10;

const STATUS_OPTIONS = [
  { value: "pending", label: "pending" },
  { value: "running", label: "running" },
  { value: "failed", label: "failed" },
  { value: "success", label: "success" }
];

const SOURCE_OPTIONS = [
  { value: "file", label: "Local File" },
  { value: "url", label: "Remote URL" }
];

const PROCESS_MODE_OPTIONS = [
  { value: "chunk", label: "直接分块" },
  { value: "pipeline", label: "数据通道" }
];

const NO_CHUNK_VALUE = -1;

const parseChunkConfig = (raw?: string | null): Record<string, unknown> => {
  if (!raw) return {};
  try {
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object") {
      return parsed as Record<string, unknown>;
    }
    return {};
  } catch {
    return {};
  }
};

const statusDotClass = (status?: string | null) => {
  if (!status) return "bg-muted-foreground/40";
  const normalized = status.toLowerCase();
  if (normalized === "success") return "bg-emerald-500";
  if (normalized === "failed") return "bg-red-500";
  if (normalized === "running") return "bg-amber-500";
  if (normalized === "pending") return "bg-slate-400";
  return "bg-muted-foreground/40";
};

const formatSize = (size?: number | null) => {
  if (!size && size !== 0) return "-";
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${parseFloat((size / 1024).toFixed(1))} KB`;
  if (size < 1024 * 1024 * 1024) return `${parseFloat((size / 1024 / 1024).toFixed(1))} MB`;
  return `${parseFloat((size / 1024 / 1024 / 1024).toFixed(1))} GB`;
};

const parseFrontMatter = (content: string): { head: string | null; body: string } => {
  if (content.startsWith("---\n")) {
    const end = content.indexOf("\n---\n", 4);
    if (end > 0) {
      return { head: content.substring(4, end), body: content.substring(end + 5) };
    }
  }
  return { head: null, body: content };
};

const formatSourceLabel = (sourceType?: string | null) => {
  const normalized = sourceType?.toLowerCase();
  if (normalized === "url") return "Remote URL";
  if (normalized === "file") return "Local File";
  return "-";
};

const ProcessModeCell = ({ doc, pipelineMap }: { doc: KnowledgeDocument; pipelineMap: Map<string, string> }) => {
  const mode = doc.processMode?.toLowerCase();
  if (mode === "chunk") {
    const detail = doc.chunkStrategy ? formatChunkStrategy(doc.chunkStrategy) : null;
    const trigger = <span className="cursor-default text-sm">Chunk</span>;
    if (!detail) return trigger;
    return (
      <TooltipProvider delayDuration={300}>
        <Tooltip>
          <TooltipTrigger asChild>{trigger}</TooltipTrigger>
          <TooltipContent><p>策略：{detail}</p></TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }
  if (mode === "pipeline") {
    const pid = doc.pipelineId ? String(doc.pipelineId) : null;
    const name = pid ? pipelineMap.get(pid) : null;
    return (
      <TooltipProvider delayDuration={300}>
        <Tooltip>
          <TooltipTrigger asChild>
            <span className="cursor-default text-sm">Data Pipeline</span>
          </TooltipTrigger>
          {name ? (
            <TooltipContent><p>{name}</p></TooltipContent>
          ) : null}
        </Tooltip>
      </TooltipProvider>
    );
  }
  return <span className="text-muted-foreground/35 text-sm">-</span>;
};

const formatChunkStrategy = (strategy?: string | null) => {
  const normalized = strategy?.toLowerCase();
  if (normalized === "fixed_size") return "固定大小";
  if (normalized === "structure_aware") return "语义感知（Markdown友好）";
  return strategy || "-";
};

const FILE_TYPE_MAP: Record<string, { icon: typeof FileText; color: string }> = {
  pdf:         { icon: FileText, color: "text-red-500" },
  markdown:    { icon: FileText, color: "text-blue-500" },
  md:          { icon: FileText, color: "text-blue-500" },
  doc:         { icon: FileText, color: "text-blue-600" },
  docx:        { icon: FileText, color: "text-blue-600" },
  txt:         { icon: FileText, color: "text-slate-500" },
  csv:         { icon: FileText, color: "text-emerald-500" },
  image:       { icon: Image,   color: "text-emerald-500" },
  png:         { icon: Image,   color: "text-emerald-500" },
  jpg:         { icon: Image,   color: "text-emerald-500" },
  jpeg:        { icon: Image,   color: "text-emerald-500" },
  gif:         { icon: Image,   color: "text-emerald-500" },
  webp:        { icon: Image,   color: "text-emerald-500" },
  svg:         { icon: Image,   color: "text-emerald-500" },
};

const renderFileTypeIcon = (fileType?: string | null, sourceType?: string | null) => {
  const type = fileType?.toLowerCase();
  if (type && FILE_TYPE_MAP[type]) {
    const { icon: Icon, color } = FILE_TYPE_MAP[type];
    return <Icon className={`h-4 w-4 shrink-0 ${color}`} />;
  }
  if (sourceType?.toLowerCase() === "url") {
    return <LinkIcon className="h-4 w-4 shrink-0 text-purple-500" />;
  }
  return <FileText className="h-4 w-4 shrink-0 text-slate-400" />;
};

export function KnowledgeDocumentsPage() {
  const { kbId } = useParams();
  const navigate = useNavigate();
  const [kb, setKb] = useState<KnowledgeBase | null>(null);
  const [pageData, setPageData] = useState<PageResult<KnowledgeDocument> | null>(null);
  const [current, setCurrent] = useState(1);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [keyword, setKeyword] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [uploadOpen, setUploadOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<KnowledgeDocument | null>(null);
  const [chunkTarget, setChunkTarget] = useState<KnowledgeDocument | null>(null);
  const [detailTarget, setDetailTarget] = useState<KnowledgeDocument | null>(null);
  const [detailName, setDetailName] = useState("");
  const [detailSaving, setDetailSaving] = useState(false);
  const [detailProcessMode, setDetailProcessMode] = useState("chunk");
  const [detailChunkStrategy, setDetailChunkStrategy] = useState("structure_aware");
  const [detailPipelineId, setDetailPipelineId] = useState("");
  const [detailStrategies, setDetailStrategies] = useState<ChunkStrategyOption[]>([]);
  const [detailPipelines, setDetailPipelines] = useState<IngestionPipeline[]>([]);
  const [detailConfigValues, setDetailConfigValues] = useState<Record<string, string>>({});
  const [detailNoChunk, setDetailNoChunk] = useState(false);
  const [detailOriginalChunkSize, setDetailOriginalChunkSize] = useState("512");
  const [detailSourceLocation, setDetailSourceLocation] = useState("");
  const [detailScheduleEnabled, setDetailScheduleEnabled] = useState(false);
  const [detailScheduleCron, setDetailScheduleCron] = useState("");
  const [logTarget, setLogTarget] = useState<KnowledgeDocument | null>(null);
  const [logData, setLogData] = useState<PageResult<KnowledgeDocumentChunkLog> | null>(null);
  const [logLoading, setLogLoading] = useState(false);
  const [previewTarget, setPreviewTarget] = useState<KnowledgeDocument | null>(null);
  const [previewContent, setPreviewContent] = useState("");
  const [previewLoading, setPreviewLoading] = useState(false);

  const documents = pageData?.records || [];
  const [pipelineMap, setPipelineMap] = useState<Map<string, string>>(new Map());
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [batchOperating, setBatchOperating] = useState(false);
  const [batchDeleteOpen, setBatchDeleteOpen] = useState(false);

  useEffect(() => {
    getIngestionPipelines(1, 200).then(r => {
      const map = new Map<string, string>();
      (r.records || []).forEach(p => map.set(String(p.id), p.name));
      setPipelineMap(map);
    }).catch(() => {});
  }, []);

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (documents.length === 0) return;
    if (selectedIds.size === documents.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(documents.map((d) => String(d.id))));
    }
  };

  const handleBatchChunk = async () => {
    if (selectedIds.size === 0) return;
    setBatchOperating(true);
    let done = 0;
    try {
      for (const id of selectedIds) {
        await startDocumentChunk(id);
        done++;
      }
      toast.success(`已触发 ${done} 个文档分块`);
      setSelectedIds(new Set());
      await loadDocuments(current, statusFilter, keyword);
    } catch (error) {
      toast.error(getErrorMessage(error, `已处理 ${done}/${selectedIds.size}，操作中断`));
    } finally {
      setBatchOperating(false);
    }
  };

  const handleBatchDelete = async () => {
    if (selectedIds.size === 0) return;
    setBatchOperating(true);
    let done = 0;
    try {
      for (const id of selectedIds) {
        await deleteDocument(id);
        done++;
      }
      toast.success(`已删除 ${done} 个文档`);
      setSelectedIds(new Set());
      setCurrent(1);
      await loadDocuments(1, statusFilter, keyword);
    } catch (error) {
      toast.error(getErrorMessage(error, `已处理 ${done}/${selectedIds.size}，操作中断`));
    } finally {
      setBatchOperating(false);
    }
  };

  const loadKnowledgeBase = async () => {
    if (!kbId) return;
    try {
      const data = await getKnowledgeBase(kbId);
      setKb(data);
    } catch (error) {
      toast.error(getErrorMessage(error, "加载知识库失败"));
      console.error(error);
    }
  };

  const loadDocuments = async (page = current, status = statusFilter, keywordValue = keyword) => {
    if (!kbId) return;
    setLoading(true);
    try {
      const data = await getDocumentsPage(kbId, {
        current: page,
        size: PAGE_SIZE,
        status,
        keyword: keywordValue || undefined
      });
      setPageData(data);
    } catch (error) {
      toast.error(getErrorMessage(error, "加载文档失败"));
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadKnowledgeBase();
  }, [kbId]);

  useEffect(() => {
    loadDocuments();
  }, [kbId, current, statusFilter, keyword]);

  useEffect(() => {
    if (detailTarget) {
      setDetailName(detailTarget.docName || "");
      const mode = (detailTarget.processMode || "chunk").toLowerCase();
      setDetailProcessMode(mode);
      setDetailChunkStrategy((detailTarget.chunkStrategy || "structure_aware").toLowerCase());
      setDetailPipelineId(detailTarget.pipelineId ? String(detailTarget.pipelineId) : "");
      setDetailSourceLocation(detailTarget.sourceLocation || "");
      setDetailScheduleEnabled(Boolean(detailTarget.scheduleEnabled));
      setDetailScheduleCron(detailTarget.scheduleCron || "");

      // 从文档的 chunkConfig JSON 解析参数值
      const config = parseChunkConfig(detailTarget.chunkConfig);
      const values: Record<string, string> = {};
      for (const [k, v] of Object.entries(config)) {
        values[k] = String(v);
      }
      setDetailConfigValues(values);

      // 如果 chunkSize 为 -1（不分块），初始化开关状态
      const rawChunkSize = values["chunkSize"];
      if (rawChunkSize === String(NO_CHUNK_VALUE)) {
        setDetailNoChunk(true);
        setDetailOriginalChunkSize("512");
      } else {
        setDetailNoChunk(false);
        setDetailOriginalChunkSize(rawChunkSize || "512");
      }

      // 加载策略列表和管道列表
      getChunkStrategies().then(setDetailStrategies).catch(() => {});
      getIngestionPipelines(1, 100).then(r => setDetailPipelines(r.records || [])).catch(() => {});
    } else {
      setDetailName("");
      setDetailProcessMode("chunk");
      setDetailChunkStrategy("structure_aware");
      setDetailPipelineId("");
      setDetailConfigValues({});
      setDetailStrategies([]);
      setDetailPipelines([]);
      setDetailSourceLocation("");
      setDetailScheduleEnabled(false);
      setDetailScheduleCron("");
      setDetailNoChunk(false);
      setDetailOriginalChunkSize("512");
    }
  }, [detailTarget]);

  const handleSearch = () => {
    setCurrent(1);
    setKeyword(searchInput.trim());
  };

  const handleRefresh = () => {
    setCurrent(1);
    loadDocuments(1, statusFilter, keyword);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteDocument(String(deleteTarget.id));
      toast.success("删除成功");
      setDeleteTarget(null);
      setCurrent(1);
      await loadDocuments(1, statusFilter, keyword);
    } catch (error) {
      toast.error(getErrorMessage(error, "删除失败"));
      console.error(error);
    }
  };

  const handleChunk = async () => {
    if (!chunkTarget) return;
    try {
      await startDocumentChunk(String(chunkTarget.id));
      toast.success("已开始分块");
      setChunkTarget(null);
      await loadDocuments(current, statusFilter, keyword);
    } catch (error) {
      toast.error(getErrorMessage(error, "分块失败"));
      console.error(error);
    }
  };

  const handleToggleEnabled = async (doc: KnowledgeDocument) => {
    const enabled = Boolean(doc.enabled);
    try {
      await enableDocument(String(doc.id), !enabled);
      toast.success(!enabled ? "已启用" : "已禁用");
      await loadDocuments(current, statusFilter, keyword);
    } catch (error) {
      toast.error(getErrorMessage(error, "操作失败"));
      console.error(error);
    }
  };

  const handleDetailSave = async () => {
    if (!detailTarget) return;
    const nextName = detailName.trim();
    if (!nextName) {
      toast.error("文档名称不能为空");
      return;
    }
    setDetailSaving(true);
    try {
      const data: Parameters<typeof updateDocument>[1] = {
        docName: nextName,
        processMode: detailProcessMode,
      };
      if (detailProcessMode === "chunk") {
        data.chunkStrategy = detailChunkStrategy;
        // 根据策略的 defaultConfig keys 组装 chunkConfig JSON
        const strategy = detailStrategies.find(s => s.value === detailChunkStrategy);
        if (strategy) {
          const configObj: Record<string, number> = {};
          for (const key of Object.keys(strategy.defaultConfig)) {
            configObj[key] = Number(detailConfigValues[key]) || strategy.defaultConfig[key];
          }
          data.chunkConfig = JSON.stringify(configObj);
        }
      } else {
        data.pipelineId = detailPipelineId;
      }
      // 添加定时调度相关字段（仅 URL 类型）
      if (detailTarget.sourceType?.toLowerCase() === "url") {
        if (detailSourceLocation.trim()) {
          data.sourceLocation = detailSourceLocation.trim();
        }
        data.scheduleEnabled = detailScheduleEnabled ? 1 : 0;
        if (detailScheduleCron.trim()) {
          data.scheduleCron = detailScheduleCron.trim();
        }
      }
      await updateDocument(String(detailTarget.id), data);
      toast.success("更新成功");
      await loadDocuments(current, statusFilter, keyword);
      setDetailTarget(null);
    } catch (error) {
      toast.error(getErrorMessage(error, "更新失败"));
      console.error(error);
    } finally {
      setDetailSaving(false);
    }
  };

  const loadChunkLogs = async (docId: string) => {
    setLogLoading(true);
    try {
      const data = await getChunkLogsPage(docId, 1, 1);
      setLogData(data);
    } catch (error) {
      toast.error(getErrorMessage(error, "加载分块日志失败"));
      console.error(error);
    } finally {
      setLogLoading(false);
    }
  };

  const handleOpenChunkLogs = (doc: KnowledgeDocument) => {
    setLogTarget(doc);
    loadChunkLogs(String(doc.id));
  };

  const handlePreview = async (doc: KnowledgeDocument) => {
    setPreviewTarget(doc);
    if (doc.fileType === "pdf") {
      setPreviewContent("");
      return;
    }
    setPreviewContent("");
    setPreviewLoading(true);
    try {
      const content = await previewDocument(String(doc.id));
      setPreviewContent(content);
    } catch (error) {
      toast.error(getErrorMessage(error, "加载预览失败"));
      setPreviewTarget(null);
    } finally {
      setPreviewLoading(false);
    }
  };

  const formatDuration = (ms?: number | null) => {
    if (!ms && ms !== 0) return "-";
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const formatLogStatus = (status?: string) => {
    if (status === "success") return "成功";
    if (status === "failed") return "失败";
    if (status === "running") return "进行中";
    return status || "-";
  };

  const detailSourceType = detailTarget?.sourceType?.toLowerCase();
  const detailIsUrlSource = detailSourceType === "url";
  const detailNameLabel = detailIsUrlSource ? "文档名称" : "本地文件";

  // 当策略切换时，用默认值填充配置
  const handleDetailStrategyChange = (value: string) => {
    setDetailChunkStrategy(value);
    const strategy = detailStrategies.find(s => s.value === value);
    if (strategy) {
      const values: Record<string, string> = {};
      for (const [k, v] of Object.entries(strategy.defaultConfig)) {
        values[k] = String(v);
      }
      setDetailConfigValues(values);
      setDetailNoChunk(false);
      setDetailOriginalChunkSize(
        strategy.defaultConfig["chunkSize"] !== undefined
          ? String(strategy.defaultConfig["chunkSize"])
          : "512"
      );
    }
  };

  // 处理编辑页"不分块"按钮点击
  const handleDetailNoChunkToggle = () => {
    if (detailNoChunk) {
      // 取消选中，恢复原始值
      setDetailConfigValues(v => ({ ...v, chunkSize: detailOriginalChunkSize }));
      setDetailNoChunk(false);
    } else {
      // 选中，保存当前值并设置为-1
      const currentSize = detailConfigValues["chunkSize"] || "512";
      setDetailOriginalChunkSize(currentSize);
      setDetailConfigValues(v => ({ ...v, chunkSize: String(NO_CHUNK_VALUE) }));
      setDetailNoChunk(true);
    }
  };

  // 用户手动修改块大小值时取消"不分块"状态
  const handleDetailChunkSizeChange = (value: string) => {
    setDetailConfigValues(v => ({ ...v, chunkSize: value }));
    if (detailNoChunk && value !== String(NO_CHUNK_VALUE)) {
      setDetailNoChunk(false);
    }
  };

  return (
    <div className="admin-page">
      <div className="admin-page-header">
        <div>
          <h1 className="admin-page-title">文档管理</h1>
          <p className="admin-page-subtitle">
            {kb ? `${kb.name}（${kb.collectionName}）` : kbId}
          </p>
        </div>
        <div className="admin-page-actions">
          <Button variant="outline" onClick={() => navigate("/admin/knowledge")}>
            返回知识库
          </Button>
          <Button className="admin-primary-gradient" onClick={() => setUploadOpen(true)}>
            <FileUp className="mr-2 h-4 w-4" />
            上传文档
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <CardTitle>文档列表</CardTitle>
              <CardDescription>支持筛选与分块管理</CardDescription>
            </div>
            <div className="flex flex-1 flex-wrap items-center justify-end gap-2">
              <Input
                value={searchInput}
                onChange={(event) => setSearchInput(event.target.value)}
                placeholder="搜索文档名称"
                className="max-w-xs"
              />
              <Button variant="outline" onClick={handleSearch}>
                搜索
              </Button>
              <Select
                value={statusFilter || "all"}
                onValueChange={(value) => {
                  setCurrent(1);
                  setStatusFilter(value === "all" ? undefined : value);
                }}
              >
                <SelectTrigger className="w-[160px]">
                  <SelectValue placeholder="状态" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部状态</SelectItem>
                  {STATUS_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button variant="outline" onClick={handleRefresh}>
                <RefreshCw className="mr-2 h-4 w-4" />
                刷新
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="py-8 text-center text-muted-foreground">加载中...</div>
          ) : documents.length === 0 ? (
            <div className="py-8 text-center text-muted-foreground">暂无文档</div>
          ) : (
            <Table className="min-w-[910px]">
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[40px]">
                      <Checkbox
                        checked={documents.length > 0 && selectedIds.size === documents.length}
                        onCheckedChange={toggleSelectAll}
                      />
                    </TableHead>
                    <TableHead className="w-[280px]">文档</TableHead>
                    <TableHead className="w-[110px]">状态</TableHead>
                    <TableHead className="w-[70px]">启用</TableHead>
                    <TableHead className="w-[80px]">分块数</TableHead>
                    <TableHead className="w-[120px]">处理模式</TableHead>
                    <TableHead className="w-[170px]">更新时间</TableHead>
                    <TableHead className="w-[170px] text-left">操作</TableHead>
                  </TableRow>
                </TableHeader>
              <TableBody>
                {documents.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell>
                      <Checkbox
                        checked={selectedIds.has(String(doc.id))}
                        onCheckedChange={() => toggleSelect(String(doc.id))}
                      />
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2.5 min-w-0 max-w-[320px]">
                        {renderFileTypeIcon(doc.fileType, doc.sourceType)}
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-1.5 min-w-0">
                            <button
                              type="button"
                              className="block truncate min-w-0 text-left font-medium text-slate-900 transition-colors hover:text-indigo-600 hover:underline underline-offset-4"
                              title={doc.docName || ""}
                              onClick={() => navigate(`/admin/knowledge/${kbId}/docs/${doc.id}`)}
                            >
                              {doc.docName || "-"}
                            </button>
                            {doc.chunksEdited ? (
                              <span
                                className="shrink-0 rounded-full bg-amber-50 px-1.5 py-px text-[10px] font-medium text-amber-700 ring-1 ring-amber-200"
                                title="该文档存在被手工编辑过的分块，重新分块会丢失"
                              >
                                已编辑
                              </span>
                            ) : null}
                          </div>
                          <div className="mt-0.5 truncate text-xs text-muted-foreground">
                            {[
                              doc.fileType,
                              doc.fileSize ? formatSize(doc.fileSize) : null,
                              doc.sourceType ? formatSourceLabel(doc.sourceType) : null,
                            ].filter(Boolean).join(" · ")}
                          </div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="inline-flex items-center gap-2 text-xs text-muted-foreground">
                        <span className={cn("h-2 w-2 rounded-full", statusDotClass(doc.status))} />
                        <span>{doc.status || "-"}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      {(() => {
                        const enabled = Boolean(doc.enabled);
                        return (
                          <button
                            type="button"
                            role="switch"
                            aria-checked={enabled}
                            aria-label={enabled ? "已启用，点击禁用" : "已禁用，点击启用"}
                            onClick={() => handleToggleEnabled(doc)}
                            className={cn(
                              "relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-background",
                              enabled ? "bg-blue-600" : "bg-slate-200"
                            )}
                          >
                            <span
                              className={cn(
                                "inline-block h-4 w-4 transform rounded-full bg-background shadow transition-transform",
                                enabled ? "translate-x-4" : "translate-x-1"
                              )}
                            />
                          </button>
                        );
                      })()}
                    </TableCell>
                    <TableCell>
                      {doc.chunkCount != null && doc.chunkCount > 0 ? (
                        <span className="tabular-nums">{doc.chunkCount}</span>
                      ) : (
                        <span className="text-muted-foreground/50">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <ProcessModeCell doc={doc} pipelineMap={pipelineMap} />
                    </TableCell>
                    <TableCell>
                      <RelativeTime value={doc.updateTime} updatedBy={doc.updatedBy} />
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {(doc.fileType === "markdown" || doc.fileType === "pdf") ? (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handlePreview(doc)}
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            预览
                          </Button>
                        ) : null}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={async () => {
                            try {
                              const detail = await getDocument(String(doc.id));
                              setDetailTarget(detail);
                            } catch (error) {
                              toast.error(getErrorMessage(error, "加载文档详情失败"));
                            }
                          }}
                        >
                          <Pencil className="h-4 w-4 mr-1" />
                          编辑
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setChunkTarget(doc)}
                        >
                          <PlayCircle className="h-4 w-4 mr-1" />
                          分块
                        </Button>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button size="icon" variant="ghost" className="h-8 w-8" title="更多">
                              <MoreHorizontal className="h-3.5 w-3.5" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleOpenChunkLogs(doc)}>
                              <FileBarChart className="mr-2 h-4 w-4" />
                              分块详情
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              className="text-destructive focus:text-destructive"
                              onClick={() => setDeleteTarget(doc)}
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              删除
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          {pageData ? (
            <div className="mt-4 flex flex-wrap items-center justify-between gap-2 text-sm text-slate-500">
              <span>共 {pageData.total} 条</span>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={() => setCurrent((prev) => Math.max(1, prev - 1))} disabled={pageData.current <= 1}>
                  上一页
                </Button>
                <span>
                  {pageData.current} / {pageData.pages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrent((prev) => Math.min(pageData.pages || 1, prev + 1))}
                  disabled={pageData.current >= pageData.pages}
                >
                  下一页
                </Button>
              </div>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <UploadDialog
        open={uploadOpen}
        onOpenChange={setUploadOpen}
        onSubmit={async (payload) => {
          if (!kbId) return;
          await uploadDocument(kbId, payload);
          toast.success("上传成功");
          setUploadOpen(false);
          setCurrent(1);
          await loadDocuments(1, statusFilter, keyword);
        }}
      />

      <AlertDialog open={Boolean(deleteTarget)} onOpenChange={(open) => (!open ? setDeleteTarget(null) : null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除文档？</AlertDialogTitle>
            <AlertDialogDescription>
              文档 [{deleteTarget?.docName}] 将被删除，且向量数据会清理。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground">
              删除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={batchDeleteOpen} onOpenChange={(open) => (!open ? setBatchDeleteOpen(false) : null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认批量删除？</AlertDialogTitle>
            <AlertDialogDescription>
              将删除选中的 {selectedIds.size} 个文档，且向量数据会清理。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction
              onClick={async () => {
                setBatchDeleteOpen(false);
                await handleBatchDelete();
              }}
              className="bg-destructive text-destructive-foreground"
            >
              删除 {selectedIds.size} 个文档
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={Boolean(chunkTarget)} onOpenChange={(open) => (!open ? setChunkTarget(null) : null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{chunkTarget?.chunkCount ? "重新分块？" : "开始分块？"}</AlertDialogTitle>
            <AlertDialogDescription asChild>
              <div className="space-y-2">
                {chunkTarget?.chunkCount ? (
                  <>
                    <div>文档 [{chunkTarget?.docName}] 已有 {chunkTarget.chunkCount} 个分块记录。</div>
                    <div className="font-medium text-amber-600">重新分块会清空原有 Chunk 记录及向量数据。</div>
                    {chunkTarget?.chunksEdited ? (
                      <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                        <span className="font-semibold">注意：</span>
                        该文档存在被手工编辑过的分块，重新分块会从源文件重新生成，
                        <span className="font-semibold">所有手动修改将丢失且无法恢复</span>。
                      </div>
                    ) : null}
                  </>
                ) : (
                  <div>文档 [{chunkTarget?.docName}] 将开始分块并写入向量库。</div>
                )}
              </div>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleChunk}
              className={chunkTarget?.chunksEdited ? "bg-destructive text-destructive-foreground hover:bg-destructive/90" : undefined}
            >
              {chunkTarget?.chunkCount ? "确认" : "开始"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <Dialog open={Boolean(detailTarget)} onOpenChange={(open) => (!open ? setDetailTarget(null) : null)}>
        <DialogContent className="max-h-[90vh] overflow-y-auto sidebar-scroll sm:max-w-[620px]" onOpenAutoFocus={(e) => e.preventDefault()} onCloseAutoFocus={(e) => { e.preventDefault(); requestAnimationFrame(() => (document.activeElement as HTMLElement)?.blur()); }}>
          <DialogHeader>
            <DialogTitle>编辑文档</DialogTitle>
            <DialogDescription>修改文档配置，保存后需重新分块才会生效</DialogDescription>
          </DialogHeader>
          {detailTarget ? (
            <div className="space-y-4">
              <div>
                <div className="text-sm font-medium mb-2">来源类型</div>
                <div className="flex h-9 items-center rounded-md border border-input bg-muted px-3 text-sm text-muted-foreground">
                  {formatSourceLabel(detailTarget.sourceType)}
                </div>
              </div>

              <div>
                <div className="text-sm font-medium mb-2">{detailNameLabel}</div>
                <Input value={detailName} onChange={(event) => setDetailName(event.target.value)} />
              </div>

              {detailIsUrlSource ? (
                <>
                  <div>
                    <div className="text-sm font-medium mb-2">来源地址</div>
                    <Input
                      value={detailSourceLocation}
                      onChange={(e) => setDetailSourceLocation(e.target.value)}
                      placeholder="https://example.com/document.pdf"
                    />
                  </div>
                  <div className="space-y-3 rounded-lg border p-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium">开启定时拉取</div>
                        <div className="text-sm text-muted-foreground">开启后按频率自动更新文档</div>
                      </div>
                      <Checkbox
                        checked={detailScheduleEnabled}
                        onCheckedChange={(checked) => setDetailScheduleEnabled(Boolean(checked))}
                      />
                    </div>
                    {detailScheduleEnabled ? (
                      <div>
                        <div className="text-sm font-medium mb-2">拉取频率（Cron表达式）</div>
                        <Input
                          value={detailScheduleCron}
                          onChange={(e) => setDetailScheduleCron(e.target.value)}
                          placeholder="0 0 * * * (每小时)"
                        />
                        <div className="text-sm text-muted-foreground mt-1">
                          例如：0 0 * * * (每小时)，0 0 0 * * * (每天)
                        </div>
                      </div>
                    ) : null}
                  </div>
                </>
              ) : null}

              <div>
                <div className="text-sm font-medium mb-2">处理模式</div>
                <Select value={detailProcessMode} onValueChange={setDetailProcessMode}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="chunk">分块策略</SelectItem>
                    <SelectItem value="pipeline">数据通道</SelectItem>
                  </SelectContent>
                </Select>
                <div className="text-sm text-muted-foreground mt-1">
                  分块策略：直接分块；数据通道：使用Pipeline清洗
                </div>
              </div>

              {detailProcessMode === "pipeline" ? (
                <div>
                  <div className="text-sm font-medium mb-2">数据通道</div>
                  <Select value={detailPipelineId} onValueChange={setDetailPipelineId}>
                    <SelectTrigger><SelectValue placeholder="选择数据通道" /></SelectTrigger>
                    <SelectContent>
                      {detailPipelines.map(p => (
                        <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              ) : null}

              {detailProcessMode === "chunk" ? (
                <div className="space-y-3 rounded-lg border p-3">
                  <div>
                    <div className="text-sm font-medium mb-2">分块策略</div>
                    <Select value={detailChunkStrategy} onValueChange={handleDetailStrategyChange}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        {detailStrategies.map(s => (
                          <SelectItem key={s.value} value={s.value}>{s.label || s.value}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {detailChunkStrategy === "fixed_size" ? (
                    <div className="grid gap-4 md:grid-cols-3">
                      <div>
                        <div className="text-sm font-medium mb-2">块大小</div>
                        <Input type="number" value={detailConfigValues["chunkSize"] ?? "512"}
                          onChange={e => handleDetailChunkSizeChange(e.target.value)} />
                        <div className="text-sm text-muted-foreground mt-1">字符数</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium mb-2">重叠大小</div>
                        <Input type="number" value={detailConfigValues["overlapSize"] ?? "128"}
                          onChange={e => setDetailConfigValues(v => ({ ...v, overlapSize: e.target.value }))} />
                      </div>
                      <div>
                        <div className="text-sm font-medium mb-2">不分块</div>
                        <div className="flex h-9 items-center">
                          <button
                            type="button"
                            role="switch"
                            aria-checked={detailNoChunk}
                            onClick={handleDetailNoChunkToggle}
                            className={cn(
                              "relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-background",
                              detailNoChunk ? "bg-blue-600" : "bg-slate-200"
                            )}
                          >
                            <span
                              className={cn(
                                "inline-block h-4 w-4 transform rounded-full bg-background shadow transition-transform",
                                detailNoChunk ? "translate-x-4" : "translate-x-1"
                              )}
                            />
                          </button>
                        </div>
                        <div className="text-sm text-muted-foreground mt-1">开启后块大小为-1</div>
                      </div>
                    </div>
                  ) : (
                    <div className="grid gap-4 md:grid-cols-2">
                      <div>
                        <div className="text-sm font-medium mb-2">理想块大小</div>
                        <Input type="number" value={detailConfigValues["targetChars"] ?? "1400"}
                          onChange={e => setDetailConfigValues(v => ({ ...v, targetChars: e.target.value }))} />
                      </div>
                      <div>
                        <div className="text-sm font-medium mb-2">块上限</div>
                        <Input type="number" value={detailConfigValues["maxChars"] ?? "1800"}
                          onChange={e => setDetailConfigValues(v => ({ ...v, maxChars: e.target.value }))} />
                      </div>
                      <div>
                        <div className="text-sm font-medium mb-2">块下限</div>
                        <Input type="number" value={detailConfigValues["minChars"] ?? "600"}
                          onChange={e => setDetailConfigValues(v => ({ ...v, minChars: e.target.value }))} />
                      </div>
                      <div>
                        <div className="text-sm font-medium mb-2">重叠大小</div>
                        <Input type="number" value={detailConfigValues["overlapChars"] ?? "0"}
                          onChange={e => setDetailConfigValues(v => ({ ...v, overlapChars: e.target.value }))} />
                      </div>
                    </div>
                  )}
                </div>
              ) : null}
            </div>
          ) : null}
          <DialogFooter>
            <Button variant="outline" onClick={() => setDetailTarget(null)} disabled={detailSaving}>
              关闭
            </Button>
            <Button
              onClick={handleDetailSave}
              disabled={detailSaving || !detailName.trim()}
            >
              {detailSaving ? "保存中..." : "保存"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={Boolean(previewTarget)} onOpenChange={(open) => (!open ? setPreviewTarget(null) : null)}>
        <DialogContent hideClose className={
          previewTarget?.fileType === "pdf"
            ? "flex h-[92vh] flex-col overflow-hidden sm:max-w-[1100px] p-0"
            : "flex max-h-[90vh] flex-col overflow-hidden sm:max-w-[900px] p-0"
        } onOpenAutoFocus={(e) => e.preventDefault()} onCloseAutoFocus={(e) => { e.preventDefault(); requestAnimationFrame(() => (document.activeElement as HTMLElement)?.blur()); }}>
          <div className="sticky top-0 z-10 flex items-center justify-between border-b bg-card px-6 py-3">
            <span className="text-sm font-medium text-muted-foreground truncate">{previewTarget?.docName || "预览"}</span>
            <DialogClose className="rounded-md p-1.5 opacity-50 transition-all hover:opacity-100 hover:bg-muted focus-visible:outline-none">
              <X className="h-3.5 w-3.5" />
            </DialogClose>
          </div>
          {previewLoading ? (
            <div className="py-8 text-center text-muted-foreground">加载中...</div>
          ) : previewTarget?.fileType === "pdf" ? (
            <iframe
              className="flex-1 w-full border-0"
              src={`${import.meta.env.VITE_API_BASE_URL || ""}/knowledge-base/docs/${previewTarget.id}/file`}
              title={previewTarget.docName || ""}
            />
          ) : previewContent ? (
            (() => {
              const { head, body } = parseFrontMatter(previewContent);
              return (
                <div className="flex-1 overflow-y-auto sidebar-scroll">
                  {head ? (
                    <pre className="mx-6 mt-4 overflow-auto rounded-lg border bg-slate-50 px-4 py-3 font-mono text-xs leading-relaxed text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400">
                      {head}
                    </pre>
                  ) : null}
                  <div className="px-6 py-4">
                    <MarkdownRenderer content={body} />
                  </div>
                </div>
              );
            })()
          ) : null}
        </DialogContent>
      </Dialog>

      <Dialog open={Boolean(logTarget)} onOpenChange={(open) => (!open ? setLogTarget(null) : null)}>
        <DialogContent className="max-h-[90vh] overflow-y-auto sidebar-scroll sm:max-w-[800px]" onOpenAutoFocus={(e) => e.preventDefault()} onCloseAutoFocus={(e) => { e.preventDefault(); requestAnimationFrame(() => (document.activeElement as HTMLElement)?.blur()); }}>
          <DialogHeader>
            <DialogTitle>分块详情</DialogTitle>
            <DialogDescription>
              文档 [{logTarget?.docName}] 的分块执行日志
            </DialogDescription>
          </DialogHeader>
          {logLoading ? (
            <div className="py-8 text-center text-muted-foreground">加载中...</div>
          ) : logData && logData.records.length > 0 ? (
            <div className="space-y-4">
              {logData.records.slice(0, 1).map((log) => {
                const isPipelineLog = log.processMode?.toLowerCase() === "pipeline";
                const chunkLabel = isPipelineLog ? "数据通道耗时" : "分块耗时";
                return (
                <div key={log.id} className="space-y-4">
                  {/* 状态 + 基本信息 */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className={cn(
                        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
                        log.status === "success" ? "bg-emerald-50 text-emerald-700" :
                        log.status === "failed" ? "bg-red-50 text-red-700" :
                        "bg-amber-50 text-amber-700"
                      )}>
                        {formatLogStatus(log.status)}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        {log.processMode === "pipeline" ? "数据通道" : "直接分块"}
                        {log.processMode === "chunk" && log.chunkStrategy ? ` · ${formatChunkStrategy(log.chunkStrategy)}` : ""}
                        {log.processMode === "pipeline" && (log.pipelineName || log.pipelineId) ? ` · ${log.pipelineName || log.pipelineId}` : ""}
                      </span>
                    </div>
                    <span className="text-2xl font-semibold tabular-nums">{log.chunkCount ?? 0} <span className="text-sm font-normal text-muted-foreground">块</span></span>
                  </div>

                  {/* 耗时指标卡片 */}
                  <div className={cn("grid gap-3", isPipelineLog ? "grid-cols-2 md:grid-cols-3" : "grid-cols-2 md:grid-cols-3 lg:grid-cols-4")}>
                    {!isPipelineLog && (
                      <div className="rounded-lg border bg-slate-50/50 p-3">
                        <div className="text-xs text-muted-foreground mb-1">文本提取</div>
                        <div className="text-lg font-semibold tabular-nums">{formatDuration(log.extractDuration)}</div>
                      </div>
                    )}
                    <div className="rounded-lg border bg-slate-50/50 p-3">
                      <div className="text-xs text-muted-foreground mb-1">{chunkLabel}</div>
                      <div className="text-lg font-semibold tabular-nums">{formatDuration(log.chunkDuration)}</div>
                    </div>
                    {!isPipelineLog && (
                      <div className="rounded-lg border bg-slate-50/50 p-3">
                        <div className="text-xs text-muted-foreground mb-1">向量化</div>
                        <div className="text-lg font-semibold tabular-nums">{formatDuration(log.embedDuration)}</div>
                      </div>
                    )}
                    <div className="rounded-lg border bg-slate-50/50 p-3">
                      <div className="text-xs text-muted-foreground mb-1">持久化</div>
                      <div className="text-lg font-semibold tabular-nums">{formatDuration(log.persistDuration)}</div>
                    </div>
                    <div className="rounded-lg border bg-slate-50/50 p-3">
                      <div className="text-xs text-muted-foreground mb-1">其他</div>
                      <div className="text-lg font-semibold tabular-nums">{formatDuration(log.otherDuration)}</div>
                    </div>
                    <div className="rounded-lg border bg-blue-50 p-3">
                      <div className="text-xs text-blue-600 mb-1">总耗时</div>
                      <div className="text-lg font-bold tabular-nums text-blue-600">{formatDuration(log.totalDuration)}</div>
                    </div>
                  </div>

                  {/* 执行时间 */}
                  <div className="flex items-center gap-2 text-sm text-slate-500">
                    <span>执行时间</span>
                    <span className="tabular-nums text-slate-700">{formatFullDateTime(log.startTime)}</span>
                    <span>~</span>
                    <span className="tabular-nums text-slate-700">{log.endTime ? formatFullDateTime(log.endTime) : "进行中"}</span>
                  </div>

                  {/* 错误信息 */}
                  {log.errorMessage && (
                    <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600">
                      <div className="font-medium mb-1">错误信息</div>
                      <div className="text-xs">{log.errorMessage}</div>
                    </div>
                  )}
                </div>
              )})}

            </div>
          ) : (
            <div className="py-8 text-center text-muted-foreground">暂无分块日志</div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setLogTarget(null)}>
              关闭
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      {selectedIds.size > 0 && (
        <div className="fixed inset-x-0 bottom-6 z-50 flex justify-center">
          <div className="animate-fade-up rounded-2xl bg-slate-900 px-5 py-3 text-sm text-white shadow-[0_10px_40px_rgba(0,0,0,0.15)]">
            <div className="flex items-center gap-3">
              <Check className="h-4 w-4 text-emerald-400" />
              <span className="tabular-nums font-medium">
                已选 {selectedIds.size} 项
              </span>
              <div className="mx-1 h-5 w-px bg-white/20" />
              <button
                type="button"
                onClick={handleBatchChunk}
                disabled={batchOperating}
                className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-white/80 transition-colors hover:bg-white/10 hover:text-white disabled:opacity-50"
              >
                <PlayCircle className="h-4 w-4" />
                批量分块
              </button>
              <button
                type="button"
                onClick={() => setBatchDeleteOpen(true)}
                disabled={batchOperating}
                className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-red-400 transition-colors hover:bg-white/10 hover:text-red-300 disabled:opacity-50"
              >
                <Trash2 className="h-4 w-4" />
                删除
              </button>
              <div className="mx-1 h-5 w-px bg-white/20" />
              <button
                type="button"
                onClick={() => setSelectedIds(new Set())}
                className="rounded-lg p-1.5 text-white/50 transition-colors hover:bg-white/10 hover:text-white/80"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

interface UploadDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (payload: KnowledgeDocumentUploadPayload) => Promise<void>;
}

const uploadSchema = z
  .object({
    sourceType: z.enum(["file", "url"]),
    sourceLocation: z.string().optional(),
    scheduleEnabled: z.boolean().default(false),
    scheduleCron: z.string().optional(),
    processMode: z.enum(["chunk", "pipeline"]).default("chunk"),
    chunkStrategy: z.string().optional(),
    pipelineId: z.string().optional(),
    chunkSize: z.string().optional(),
    overlapSize: z.string().optional(),
    targetChars: z.string().optional(),
    maxChars: z.string().optional(),
    minChars: z.string().optional(),
    overlapChars: z.string().optional()
  })
  .superRefine((values, ctx) => {
    const isBlank = (value?: string) => !value || value.trim() === "";
    const requireNumber = (value: string | undefined, field: keyof typeof values, label: string) => {
      if (isBlank(value)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: [field],
          message: `请输入${label}`
        });
        return;
      }
      if (Number.isNaN(Number(value))) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: [field],
          message: `${label}必须是数字`
        });
      }
    };

    if (values.sourceType === "url" && isBlank(values.sourceLocation)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["sourceLocation"],
        message: "请输入来源地址"
      });
    }
    if (values.scheduleEnabled && isBlank(values.scheduleCron)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["scheduleCron"],
        message: "请输入定时频率"
      });
    }

    if (values.processMode === "chunk") {
      if (!values.chunkStrategy) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["chunkStrategy"],
          message: "请选择分块策略"
        });
        return;
      }
      if (values.chunkStrategy === "fixed_size") {
        requireNumber(values.chunkSize, "chunkSize", "块大小");
        requireNumber(values.overlapSize, "overlapSize", "重叠大小");
      } else {
        requireNumber(values.targetChars, "targetChars", "理想块大小");
        requireNumber(values.maxChars, "maxChars", "块上限");
        requireNumber(values.minChars, "minChars", "块下限");
        requireNumber(values.overlapChars, "overlapChars", "重叠大小");
      }
    } else if (values.processMode === "pipeline") {
      if (isBlank(values.pipelineId)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["pipelineId"],
          message: "请选择数据通道"
        });
      }
    }
  });

type UploadFormValues = z.infer<typeof uploadSchema>;

function UploadDialog({ open, onOpenChange, onSubmit }: UploadDialogProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [saving, setSaving] = useState(false);
  const [chunkStrategies, setChunkStrategies] = useState<ChunkStrategyOption[]>([]);
  const [noChunk, setNoChunk] = useState(false);
  const [originalChunkSize, setOriginalChunkSize] = useState("512");
  const [pipelines, setPipelines] = useState<IngestionPipeline[]>([]);
  const [loadingPipelines, setLoadingPipelines] = useState(false);
  const [maxFileSize, setMaxFileSize] = useState<number>(50 * 1024 * 1024);

  const form = useForm<UploadFormValues>({
    resolver: zodResolver(uploadSchema),
    defaultValues: {
      sourceType: "file",
      sourceLocation: "",
      scheduleEnabled: false,
      scheduleCron: "",
      processMode: "chunk",
      chunkStrategy: "fixed_size",
      pipelineId: "",
      chunkSize: "512",
      overlapSize: "128",
      targetChars: "1400",
      maxChars: "1800",
      minChars: "600",
      overlapChars: "0"
    }
  });

  const sourceType = form.watch("sourceType");
  const processMode = form.watch("processMode");
  const chunkStrategy = form.watch("chunkStrategy");
  const scheduleEnabled = form.watch("scheduleEnabled");
  const chunkSize = form.watch("chunkSize");
  const isUrlSource = sourceType === "url";
  const isChunkMode = processMode === "chunk";
  const isPipelineMode = processMode === "pipeline";
  const isFixedSize = chunkStrategy === "fixed_size";

  const loadPipelines = async () => {
    setLoadingPipelines(true);
    try {
      const result = await getIngestionPipelines(1, 100);
      setPipelines(result.records || []);
    } catch (error) {
      console.error("加载Pipeline失败", error);
      toast.error("加载Pipeline失败");
    } finally {
      setLoadingPipelines(false);
    }
  };

  useEffect(() => {
    if (open) {
      setFile(null);
      form.reset({
        sourceType: "file",
        sourceLocation: "",
        scheduleEnabled: false,
        scheduleCron: "",
        processMode: "chunk",
        chunkStrategy: "fixed_size",
        pipelineId: "",
        chunkSize: "512",
        overlapSize: "128",
        targetChars: "1400",
        maxChars: "1800",
        minChars: "600",
        overlapChars: "0"
      });
      setNoChunk(false);
      setOriginalChunkSize("512");
      loadPipelines();
      getChunkStrategies().then(setChunkStrategies).catch(() => {});
      getSystemSettings()
        .then((settings) => setMaxFileSize(settings.upload.maxFileSize))
        .catch(() => {});
    }
  }, [open, form]);

  useEffect(() => {
    if (isUrlSource) {
      setFile(null);
    }
  }, [isUrlSource]);

  // 切换策略时，用 API 返回的默认值填充表单
  useEffect(() => {
    const strategy = chunkStrategies.find((s) => s.value === chunkStrategy);
    if (!strategy) return;
    const defaults = strategy.defaultConfig;
    const formAccessors: Record<string, (v: string) => void> = {
      chunkSize: (v) => form.setValue("chunkSize", v),
      overlapSize: (v) => form.setValue("overlapSize", v),
      targetChars: (v) => form.setValue("targetChars", v),
      maxChars: (v) => form.setValue("maxChars", v),
      minChars: (v) => form.setValue("minChars", v),
      overlapChars: (v) => form.setValue("overlapChars", v)
    };
    for (const key of Object.keys(strategy.defaultConfig)) {
      if (defaults[key] !== undefined && formAccessors[key]) {
        formAccessors[key](String(defaults[key]));
      }
    }
    if (defaults["chunkSize"] !== undefined) {
      setOriginalChunkSize(String(defaults["chunkSize"]));
    }
  }, [chunkStrategy, chunkStrategies, form]);

  // 监听块大小变化，如果用户手动修改了值，取消"不分块"状态
  useEffect(() => {
    if (noChunk && chunkSize !== String(NO_CHUNK_VALUE)) {
      setNoChunk(false);
    }
  }, [chunkSize, noChunk]);

  // 处理"不分块"按钮点击
  const handleNoChunkToggle = () => {
    if (noChunk) {
      // 取消选中，恢复原始值
      form.setValue("chunkSize", originalChunkSize);
      setNoChunk(false);
    } else {
      // 选中，保存当前值并设置为-1
      setOriginalChunkSize(chunkSize || "512");
      form.setValue("chunkSize", String(NO_CHUNK_VALUE));
      setNoChunk(true);
    }
  };

  const parseNumber = (value?: string) => {
    if (!value || !value.trim()) return null;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  };

  const handleSubmit = async (values: UploadFormValues) => {
    if (values.sourceType === "file" && !file) {
      toast.error("请选择文件");
      return;
    }
    if (values.sourceType === "file" && file && file.size > maxFileSize) {
      const sizeMB = Math.floor(maxFileSize / 1024 / 1024);
      toast.error(`上传文件大小超过限制，最大允许 ${sizeMB}MB`);
      return;
    }

    // 根据当前策略的 defaultConfig keys 从表单值组装 chunkConfig JSON
    let chunkConfig: string | undefined;
    if (values.processMode === "chunk") {
      const strategy = chunkStrategies.find((s) => s.value === values.chunkStrategy);
      if (strategy) {
        const formAccessors: Record<string, string | undefined> = {
          chunkSize: values.chunkSize,
          overlapSize: values.overlapSize,
          targetChars: values.targetChars,
          maxChars: values.maxChars,
          minChars: values.minChars,
          overlapChars: values.overlapChars
        };
        const config: Record<string, number> = {};
        for (const key of Object.keys(strategy.defaultConfig)) {
          const val = parseNumber(formAccessors[key]);
          if (val !== null) {
            config[key] = val;
          }
        }
        chunkConfig = JSON.stringify(config);
      }
    }

    setSaving(true);
    try {
      const payload: KnowledgeDocumentUploadPayload = {
        sourceType: values.sourceType,
        file: values.sourceType === "file" ? file : null,
        sourceLocation: values.sourceType === "url" ? values.sourceLocation.trim() : null,
        scheduleEnabled: values.sourceType === "url" ? values.scheduleEnabled : false,
        scheduleCron:
          values.sourceType === "url" && values.scheduleEnabled
            ? values.scheduleCron.trim()
            : null,
        processMode: values.processMode,
        chunkStrategy: values.processMode === "chunk" ? values.chunkStrategy : undefined,
        chunkConfig: chunkConfig ?? null,
        pipelineId: values.processMode === "pipeline" ? values.pipelineId : null
      };
      await onSubmit(payload);
    } catch (error) {
      toast.error(getErrorMessage(error, "上传失败"));
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="max-h-[90vh] overflow-y-auto sidebar-scroll sm:max-w-[620px]"
        onOpenAutoFocus={(e) => e.preventDefault()}
        onCloseAutoFocus={(e) => { e.preventDefault(); requestAnimationFrame(() => (document.activeElement as HTMLElement)?.blur()); }}
      >
        <DialogHeader>
          <DialogTitle>上传文档</DialogTitle>
          <DialogDescription>支持本地文件或远程URL，并配置分块策略</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form className="space-y-4" onSubmit={form.handleSubmit(handleSubmit)}>
            <FormField
              control={form.control}
              name="sourceType"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>来源类型</FormLabel>
                  <Select value={field.value} onValueChange={field.onChange}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="选择来源类型" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {SOURCE_OPTIONS.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            {isUrlSource ? (
              <FormField
                control={form.control}
                name="sourceLocation"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>来源地址</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="https://raw.githubusercontent.com/bytedance/deer-flow/main/docs/API.md"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>填写远程文档 URL</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            ) : (
              <FormItem>
                <FormLabel>本地文件</FormLabel>
                <FormControl>
                  <div
                    className={cn(
                      "flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-6 cursor-pointer transition-colors select-none",
                      isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50",
                      file && !isDragging && "border-primary/40 bg-muted/30"
                    )}
                    onClick={() => fileInputRef.current?.click()}
                    onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                    onDragLeave={(e) => { if (!e.currentTarget.contains(e.relatedTarget as Node)) setIsDragging(false); }}
                    onDrop={(e) => {
                      e.preventDefault();
                      setIsDragging(false);
                      const dropped = e.dataTransfer.files[0];
                      if (dropped) setFile(dropped);
                    }}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      className="hidden"
                      onChange={(e) => setFile(e.target.files?.[0] || null)}
                    />
                    {file ? (
                      <>
                        <FileUp className="h-7 w-7 text-primary" />
                        <div className="text-sm font-medium text-center break-all px-2">{file.name}</div>
                        <div className="text-xs text-muted-foreground">{formatSize(file.size)}</div>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="h-7 px-2 text-xs text-muted-foreground hover:text-foreground"
                          onClick={(e) => { e.stopPropagation(); setFile(null); if (fileInputRef.current) fileInputRef.current.value = ""; }}
                        >
                          <X className="h-3 w-3 mr-1" />
                          重新选择
                        </Button>
                      </>
                    ) : (
                      <>
                        <FileUp className="h-7 w-7 text-muted-foreground" />
                        <div className="text-sm font-medium">拖拽文件到此处，或点击选择</div>
                        <div className="text-xs text-muted-foreground">支持 PDF、Markdown、Word、TXT 等格式</div>
                      </>
                    )}
                  </div>
                </FormControl>
              </FormItem>
            )}

            {isUrlSource ? (
              <div className="space-y-3 rounded-lg border p-3">
                <FormField
                  control={form.control}
                  name="scheduleEnabled"
                  render={({ field }) => (
                    <FormItem className="flex items-center justify-between">
                      <div>
                        <FormLabel>开启定时拉取</FormLabel>
                        <FormDescription>开启后按频率自动更新文档</FormDescription>
                      </div>
                      <FormControl>
                        <Checkbox checked={field.value} onCheckedChange={(value) => field.onChange(Boolean(value))} />
                      </FormControl>
                    </FormItem>
                  )}
                />
                {scheduleEnabled ? (
                  <FormField
                    control={form.control}
                    name="scheduleCron"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>拉取频率</FormLabel>
                        <FormControl>
                          <Input placeholder="例如：0 0 0 * * ?" {...field} />
                        </FormControl>
                        <FormDescription>支持 cron 表达式，例如每天凌晨</FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                ) : null}
              </div>
            ) : null}

            <div className="space-y-3 rounded-lg border p-3">
              <FormField
                control={form.control}
                name="processMode"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>处理模式</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="选择处理模式" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {PROCESS_MODE_OPTIONS.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {isPipelineMode ? (
                <FormField
                  control={form.control}
                  name="pipelineId"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-xs text-muted-foreground font-normal">选择通道</FormLabel>
                      <Select value={field.value} onValueChange={field.onChange} disabled={loadingPipelines}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder={loadingPipelines ? "加载中..." : "请选择"} />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {pipelines.length > 0 ? (
                            pipelines.map((pipeline) => (
                              <SelectItem key={pipeline.id} value={pipeline.id}>
                                {pipeline.name}
                              </SelectItem>
                            ))
                          ) : (
                            <div className="py-6 text-center text-sm text-muted-foreground">
                              暂无数据通道
                            </div>
                          )}
                        </SelectContent>
                      </Select>
                      <FormDescription>通过ETL处理提升文件数据质量，增强向量搜索效果</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              ) : null}

              {isChunkMode ? (
                <div className="space-y-3">
                  <FormField
                    control={form.control}
                    name="chunkStrategy"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs text-muted-foreground font-normal">切分方式</FormLabel>
                        <Select value={field.value} onValueChange={field.onChange}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="选择切分方式" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {chunkStrategies.map((option) => (
                              <SelectItem key={option.value} value={option.value}>
                                {option.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

              {isFixedSize ? (
                <>
                  <div className="grid gap-4 md:grid-cols-3">
                    <FormField
                      control={form.control}
                      name="chunkSize"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-xs text-muted-foreground font-normal">块大小</FormLabel>
                          <FormControl>
                            <Input type="number" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="overlapSize"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-xs text-muted-foreground font-normal">重叠大小</FormLabel>
                          <FormControl>
                            <Input type="number" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormItem>
                      <FormLabel className="text-xs text-muted-foreground font-normal">不分块</FormLabel>
                      <FormControl>
                        <div className="flex h-9 items-center">
                          <button
                            type="button"
                            role="switch"
                            aria-checked={noChunk}
                            onClick={handleNoChunkToggle}
                            className={cn(
                              "relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-background",
                              noChunk ? "bg-blue-600" : "bg-slate-200"
                            )}
                          >
                            <span
                              className={cn(
                                "inline-block h-4 w-4 transform rounded-full bg-background shadow transition-transform",
                                noChunk ? "translate-x-4" : "translate-x-1"
                              )}
                            />
                          </button>
                        </div>
                      </FormControl>
                      <FormDescription>开启后块大小为-1</FormDescription>
                    </FormItem>
                  </div>
                </>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  <FormField
                    control={form.control}
                    name="targetChars"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs text-muted-foreground font-normal">理想块大小</FormLabel>
                        <FormControl>
                          <Input type="number" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="maxChars"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs text-muted-foreground font-normal">块上限</FormLabel>
                        <FormControl>
                          <Input type="number" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="minChars"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs text-muted-foreground font-normal">块下限</FormLabel>
                        <FormControl>
                          <Input type="number" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="overlapChars"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs text-muted-foreground font-normal">重叠大小</FormLabel>
                        <FormControl>
                          <Input type="number" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              )}
            </div>
            ) : null}
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => onOpenChange(false)} disabled={saving}>
                取消
              </Button>
              <Button type="submit" disabled={saving}>
                {saving ? "上传中..." : "上传"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
