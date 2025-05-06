import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';

function Content() {
  const location = useLocation();
  const { module, submodule } = location.state || {};
  const [htmlContent, setHtmlContent] = useState('');

  useEffect(() => {
    const fetchContent = async () => {
      try {
        console.log(module , submodule);
        const response = await axios.get('/content', {
          params: { module, submodule }
        });
        setHtmlContent(response.data.content);
      } catch (error) {
        console.error('Failed to fetch content:', error);
      }
    };
    if (module && submodule) {
      fetchContent();
    }
  }, [module, submodule]);

  return (
    <div className="rendered-html" dangerouslySetInnerHTML={{ __html: htmlContent }} />
  );
}

export default Content;