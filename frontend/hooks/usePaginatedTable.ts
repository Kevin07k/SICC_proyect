"use client";

import { useMemo, useState } from "react";

export interface PaginatedTableOptions<T> {
  pageSize?: number;
  searchKeys?: (keyof T | ((row: T) => string))[];
}

export function usePaginatedTable<T>(
  rows: T[],
  options: PaginatedTableOptions<T> = {},
) {
  const { pageSize = 10, searchKeys = [] } = options;
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((row) => {
      const values = searchKeys.map((key) => {
        if (typeof key === "function") return key(row);
        const v = row[key];
        return v != null ? String(v) : "";
      });
      return values.some((v) => v.toLowerCase().includes(q));
    });
  }, [rows, search, searchKeys]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const currentPage = Math.min(page, totalPages);

  const paginated = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filtered.slice(start, start + pageSize);
  }, [filtered, currentPage, pageSize]);

  const setSearchSafe = (value: string) => {
    setSearch(value);
    setPage(1);
  };

  const rangeStart = filtered.length === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const rangeEnd = Math.min(currentPage * pageSize, filtered.length);

  return {
    search,
    setSearch: setSearchSafe,
    page: currentPage,
    setPage,
    totalPages,
    paginated,
    filtered,
    total: filtered.length,
    rangeStart,
    rangeEnd,
  };
}
