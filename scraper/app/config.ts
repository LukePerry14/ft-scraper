import 'dotenv/config';
import path from 'node:path';
import os from 'node:os';

export const config = {
  loginUrl: 'https://www.ft.com/login',
  storageStatePath: process.env.STORAGE_STATE_PATH? os.homedir() + process.env.STORAGE_STATE_PATH: path.resolve('storage-state.json'),
  homeTitle: "Home - Financial Times",
  homeURL: "https://www.ft.com",
  tmpStorage: "../storage",
  maxBackoff: 10,
};
