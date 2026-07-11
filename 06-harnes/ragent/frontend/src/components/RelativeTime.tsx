import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { formatRelativeTime, formatTooltipTime } from "@/utils/time";

interface RelativeTimeProps {
  value?: string | null;
  updatedBy?: string | null;
}

export function RelativeTime({ value, updatedBy }: RelativeTimeProps) {
  if (!value) return <span className="text-muted-foreground/35">-</span>;

  const display = updatedBy
    ? `${updatedBy} · ${formatRelativeTime(value)}`
    : formatRelativeTime(value);

  return (
    <TooltipProvider delayDuration={300}>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className="cursor-default truncate text-sm tabular-nums">
            {display}
          </span>
        </TooltipTrigger>
        <TooltipContent>
          <p>{formatTooltipTime(value)}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
