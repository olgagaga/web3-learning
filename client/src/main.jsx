import React from 'react'
import ReactDOM from 'react-dom/client'
import { ThirdwebProvider } from '@thirdweb-dev/react'
import App from './App.jsx'
import './styles/index.css'

const activeChain = 'sepolia' // Using Sepolia testnet

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThirdwebProvider
      activeChain={activeChain}
      clientId={import.meta.env.VITE_THIRDWEB_CLIENT_ID}
    >
      <App />
    </ThirdwebProvider>
  </React.StrictMode>,
)
