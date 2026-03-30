import { Button } from "@/components/ui/button";
import type { Pagination } from "@/types/api";

interface PaginationControlsProps {
  pagination: Pagination;
  onPageChange: (nextPage: number) => void;
  onPageSizeChange: (nextPageSize: number) => void;
  pageSizeOptions?: number[];
}

const DEFAULT_PAGE_SIZE_OPTIONS = [12, 24, 48, 96];

export function PaginationControls({
  pagination,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = DEFAULT_PAGE_SIZE_OPTIONS,
}: PaginationControlsProps) {
  const safeCurrentPage = Math.max(1, pagination.currentPage);
  const safeTotalPages = Math.max(1, pagination.totalPages);

  return (
    <div className="mb-6 flex flex-wrap items-center justify-between gap-3 rounded-lg border bg-background/60 p-3">
      <p className="text-muted-foreground text-sm">
        Page {safeCurrentPage} of {safeTotalPages} · {pagination.totalItems}{" "}
        total instances
      </p>
      <div className="flex flex-wrap items-center gap-2">
        <label
          htmlFor="pagination-page-size"
          className="text-muted-foreground text-xs uppercase tracking-wide"
        >
          Per page
        </label>
        <select
          id="pagination-page-size"
          value={String(pagination.pageSize)}
          onChange={(event) => onPageSizeChange(Number(event.target.value))}
          className="h-8 rounded-md border bg-background px-2 text-sm"
        >
          {pageSizeOptions.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>

        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={!pagination.hasPreviousPage}
          onClick={() => onPageChange(safeCurrentPage - 1)}
        >
          Previous
        </Button>
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={!pagination.hasNextPage}
          onClick={() => onPageChange(safeCurrentPage + 1)}
        >
          Next
        </Button>
      </div>
    </div>
  );
}
