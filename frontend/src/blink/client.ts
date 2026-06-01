import { PhantomWalletAdapter } from '@solana/wallet-adapter-wallets'
import { Connection, clusterApiUrl } from '@solana/web3.js'

export const connection = new Connection(clusterApiUrl('devnet'), 'confirmed')
export const wallets = [new PhantomWalletAdapter()]
