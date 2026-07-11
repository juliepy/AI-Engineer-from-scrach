import { format, differenceInMinutes, differenceInHours, differenceInDays } from "date-fns";

const WEEKDAY_NAMES = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];

const getWeekStart = (d: Date) => {
  const date = new Date(d);
  const day = date.getDay();
  const diff = day === 0 ? 6 : day - 1;
  date.setDate(date.getDate() - diff);
  date.setHours(0, 0, 0, 0);
  return date;
};

const formatRelativeNumeric = (value: string) => {
  const date = new Date(value);
  const diffMinutes = differenceInMinutes(new Date(), date);
  const diffHours = differenceInHours(new Date(), date);
  const diffDays = differenceInDays(new Date(), date);
  if (diffMinutes < 1) return "刚刚";
  if (diffMinutes < 60) return `${diffMinutes} 分钟前`;
  if (diffHours < 24) return `${diffHours} 小时前`;
  return `${diffDays} 天前`;
};

export const formatRelativeTime = (value?: string | null) => {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const now = new Date();
  const diffMinutes = differenceInMinutes(now, date);
  const diffHours = differenceInHours(now, date);
  if (diffMinutes < 1) return "刚刚";
  if (diffMinutes < 60) return `${diffMinutes} 分钟前`;
  if (date.getDate() === now.getDate() && date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear()) {
    return `${diffHours} 小时前`;
  }
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  if (date.getDate() === yesterday.getDate() && date.getMonth() === yesterday.getMonth() && date.getFullYear() === yesterday.getFullYear()) {
    return `昨天 ${format(date, "HH:mm")}`;
  }
  const weekStart = getWeekStart(now);
  if (date >= weekStart) {
    return `${WEEKDAY_NAMES[date.getDay()]} ${format(date, "HH:mm")}`;
  }
  if (date.getFullYear() === now.getFullYear()) {
    return format(date, "M月d日");
  }
  return format(date, "yyyy年M月d日");
};

export const formatFullDateTime = (value?: string | null) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return format(date, "yyyy-MM-dd HH:mm:ss");
};

export const formatTooltipTime = (value?: string | null) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${format(date, "yyyy-MM-dd HH:mm:ss")} · ${formatRelativeNumeric(value)}`;
};
