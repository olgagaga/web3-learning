import { useAddress, useDisconnect, useConnect, ConnectWallet } from '@thirdweb-dev/react'
import { useEffect } from 'react'
import { useWeb3Store } from '../../stores/web3Store'

function WalletButton() {
  const address = useAddress()
  const disconnect = useDisconnect()
  const { setWallet, disconnect: storeDisconnect } = useWeb3Store()

  useEffect(() => {
    if (address) {
      setWallet(address, '0')
    } else {
      storeDisconnect()
    }
  }, [address, setWallet, storeDisconnect])

  const handleDisconnect = async () => {
    await disconnect()
    storeDisconnect()
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
            className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-sm font-medium"
          >
            Disconnect
          </button>
        </div>
      ) : (
        <ConnectWallet
          theme="light"
          btnTitle="Connect Wallet"
          className="!px-4 !py-2 !bg-primary !text-white !rounded-lg !font-medium"
        />
      )}
    </div>
  )
}

export default WalletButton
