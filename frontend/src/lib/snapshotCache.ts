const DB_NAME = 'vms_snapshots'
const STORE_NAME = 'snapshots'
const DB_VERSION = 1
const MAX_AGE_MS = 24 * 60 * 60 * 1000 // 24h

let dbPromise: Promise<IDBDatabase> | null = null

function openDB(): Promise<IDBDatabase> {
  if (dbPromise) return dbPromise

  dbPromise = new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)
    
    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve(request.result)
    
    request.onupgradeneeded = (e) => {
      const db = (e.target as IDBOpenDBRequest).result
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id' })
      }
    }
  })

  return dbPromise
}

export async function getSnapshot(cameraId: number): Promise<string | null> {
  try {
    const db = await openDB()
    const tx = db.transaction(STORE_NAME, 'readonly')
    const store = tx.objectStore(STORE_NAME)
    
    return new Promise((resolve) => {
      const request = store.get(`camera_${cameraId}`)
      request.onsuccess = () => {
        const data = request.result
        if (data && Date.now() - data.timestamp < MAX_AGE_MS) {
          resolve(data.snapshot)
        } else {
          resolve(null)
        }
      }
      request.onerror = () => resolve(null)
    })
  } catch {
    return null
  }
}

export async function saveSnapshot(cameraId: number, snapshot: string): Promise<void> {
  try {
    const db = await openDB()
    const tx = db.transaction(STORE_NAME, 'readwrite')
    const store = tx.objectStore(STORE_NAME)
    
    await store.put({
      id: `camera_${cameraId}`,
      snapshot,
      timestamp: Date.now()
    })
  } catch (e) {
    console.warn('Failed to cache snapshot:', e)
  }
}

export async function clearOldSnapshots(): Promise<void> {
  try {
    const db = await openDB()
    const tx = db.transaction(STORE_NAME, 'readwrite')
    const store = tx.objectStore(STORE_NAME)
    const request = store.openCursor()
    
    request.onsuccess = (e) => {
      const cursor = (e.target as IDBRequest).result
      if (cursor) {
        const data = cursor.value
        if (Date.now() - data.timestamp > MAX_AGE_MS) {
          cursor.delete()
        }
        cursor.continue()
      }
    }
  } catch {}
}
