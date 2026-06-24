export function useDateFormat() {
  function relativeTime(dateStr) {
    if (!dateStr) return null
    const now = new Date()
    const then = new Date(dateStr)
    const nowMidnight = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const thenMidnight = new Date(then.getFullYear(), then.getMonth(), then.getDate())
    const days = Math.round((nowMidnight - thenMidnight) / 86400000)
    if (days === 0) return 'Today'
    if (days === 1) return 'Yesterday'
    if (days < 7) return `${days} days ago`
    if (days < 30) return `${Math.floor(days / 7)}w ago`
    if (days < 365) return `${Math.floor(days / 30)}mo ago`
    return `${Math.floor(days / 365)}y ago`
  }

  function shortDate(dateStr) {
    if (!dateStr) return null
    return new Date(dateStr).toLocaleDateString('en-GB', {
      day: 'numeric', month: 'short', year: 'numeric',
    })
  }

  return { relativeTime, shortDate }
}
