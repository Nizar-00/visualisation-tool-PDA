
import { useEffect } from 'react';

export default function useNoPagePrecedente() {
  useEffect(() => {
    const handlePopState = () => {
      window.history.go(1);
    };

    window.history.pushState(null, null, window.location.href);
    window.addEventListener('popstate', handlePopState);

    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, []);
}
