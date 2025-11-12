import { useAddress, useDisconnect, ConnectWallet } from '@thirdweb-dev/react'
import { useEffect, useState } from 'react'
import { useWeb3Store } from '../../stores/web3Store'

function WalletButton() {
  const address = useAddress()
  const disconnect = useDisconnect()
  const { setWallet, disconnect: storeDisconnect } = useWeb3Store()
  const [isDisconnecting, setIsDisconnecting] = useState(false)
  const [connectKey, setConnectKey] = useState(0)

  useEffect(() => {
    if (address) {
      setWallet(address, '0')
      setIsDisconnecting(false)
    } else {
      storeDisconnect()
    }
  }, [address, setWallet, storeDisconnect])

  const handleDisconnect = async () => {
    setIsDisconnecting(true)
    try {
      await disconnect()
      storeDisconnect()
      // Force a small delay to ensure Thirdweb state is cleared
      setTimeout(() => {
        setIsDisconnecting(false)
        setConnectKey(prev => prev + 1) // Force ConnectWallet to re-render
      }, 500)
    } catch (error) {
      console.error('Disconnect error:', error)
      setIsDisconnecting(false)
    }
  }

  return (
    <div className="flex items-center gap-3">
      {address ? (
        <div className="flex items-center gap-2">
          <div className="px-4 py-2 bg-green-100 text-green-800 rounded-lg font-mono text-sm">
            {address.slice(0, 6)}...{address.slice(-4)}
          </div>
          <button
            onClick={handleDisconnect}
            disabled={isDisconnecting}
            className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isDisconnecting ? 'Disconnecting...' : 'Disconnect'}
          </button>
        </div>
      ) : (
        <div key={connectKey}>
          <ConnectWallet
            theme="light"
            btnTitle="Connect Wallet"
            modalTitle="Connect Your Wallet"
            modalTitleIconUrl=""
            switchToActiveChain={true}
            className="!px-4 !py-2 !bg-primary !text-white !rounded-lg !font-medium"
          />
          <p className="text-xs text-gray-500 mt-1 text-center">
            Make sure you're on Sepolia testnet
          </p>
        </div>
      )}
    </div>
  )
}

export default WalletButton
