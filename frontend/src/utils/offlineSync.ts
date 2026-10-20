/**
 * AEGIS-CLIMATE Frontend Offline Synchronization Engine
 * Module: frontend/src/utils/offlineSync.ts
 * Governance: Gravitas Reliability Runtime · Mathematical Invariant Adherence
 *
 * Invariant: State_Client ⊕ Delta_Offline ≡ State_Cloud
 * Manages local IndexedDB / LocalStorage mutation queues during catastrophic network partitions.
 */

export interface OfflineQueueRecord {
  client_record_id: string;
  entity_type: 'incident_report' | 'sensor_telemetry' | 'civic_alert' | 'gis_contour';
  created_at_epoch: number;
  payload: Record<string, any>;
  client_version?: string;
  sync_attempts?: number;
}

export interface SyncReconciliationResult {
  client_record_id: string;
  server_record_id: string;
  status: 'RECONCILED' | 'MERGED' | 'CONFLICT_OVERRIDDEN';
  message: string;
}

export interface BatchSyncResponse {
  device_id: string;
  total_received: number;
  total_processed: number;
  conflict_count: number;
  reconciliation_log: SyncReconciliationResult[];
  cloud_sync_timestamp: number;
}

const STORAGE_KEY = 'terra_sentinel_offline_queue_v2';

export class OfflineSyncEngine {
  private deviceId: string;

  constructor() {
    this.deviceId = this.getOrCreateDeviceId();
  }

  private getOrCreateDeviceId(): string {
    try {
      let id = localStorage.getItem('terra_sentinel_device_id');
      if (!id) {
        id = `DEV-${Math.random().toString(36).substring(2, 9).toUpperCase()}-${Date.now().toString(36)}`;
        localStorage.setItem('terra_sentinel_device_id', id);
      }
      return id;
    } catch {
      return `DEV-FALLBACK-${Date.now()}`;
    }
  }

  public enqueueRecord(
    entityType: OfflineQueueRecord['entity_type'],
    payload: Record<string, any>
  ): OfflineQueueRecord {
    const record: OfflineQueueRecord = {
      client_record_id: `CLI-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
      entity_type: entityType,
      created_at_epoch: Date.now() / 1000,
      payload,
      client_version: '2.0.0',
      sync_attempts: 0
    };

    const currentQueue = this.getPendingRecords();
    currentQueue.push(record);
    this.persistQueue(currentQueue);
    return record;
  }

  public getPendingRecords(): OfflineQueueRecord[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [];
      return JSON.parse(raw);
    } catch (e) {
      console.warn('Failed to parse offline sync queue from localStorage:', e);
      return [];
    }
  }

  public persistQueue(records: OfflineQueueRecord[]): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
    } catch (e) {
      console.error('Failed to persist offline sync queue:', e);
    }
  }

  public clearSyncedRecords(reconciledIds: string[]): void {
    const set = new Set(reconciledIds);
    const remaining = this.getPendingRecords().filter(r => !set.has(r.client_record_id));
    this.persistQueue(remaining);
  }

  public async syncWithCloud(apiBaseUrl: string = ''): Promise<BatchSyncResponse | null> {
    const pending = this.getPendingRecords();
    if (pending.length === 0) return null;

    try {
      const url = `${apiBaseUrl.replace(/\/$/, '')}/api/v1/sync/offline-batch`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          device_id: this.deviceId,
          synced_at_epoch: Date.now() / 1000,
          records: pending
        })
      });

      if (!response.ok) {
        throw new Error(`Sync failed with HTTP ${response.status}`);
      }

      const result: BatchSyncResponse = await response.json();
      const reconciledIds = result.reconciliation_log.map(log => log.client_record_id);
      this.clearSyncedRecords(reconciledIds);
      return result;
    } catch (err) {
      console.warn('Offline sync attempt deferred (network partition active):', err);
      return null;
    }
  }
}

export const offlineSyncEngine = new OfflineSyncEngine();
