export function formatDate(date) {
  if (!date) return "";
  return new Date(date).toLocaleDateString("zh-CN");
}

export function formatDateTime(date) {
  if (!date) return "";
  return new Date(date).toLocaleString("zh-CN");
}

export function formatRelativeTime(date) {
  if (!date) return "";
  const now = new Date();
  const target = new Date(date);
  const diff = now - target;
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) return "刚刚";
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 30) return `${days}天前`;
  return formatDate(date);
}
