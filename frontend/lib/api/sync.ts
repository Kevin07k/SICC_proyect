import { api } from "@/lib/api/client";
import type { SyncManualResponse, SyncStatusResponse } from "@/types/sync";

export function runSyncManual(): Promise<SyncManualResponse> {
  return api<SyncManualResponse>("/sync/manual", { method: "POST" });
}

export function getSyncStatus(): Promise<SyncStatusResponse> {
  return api<SyncStatusResponse>("/sync/status");
}
