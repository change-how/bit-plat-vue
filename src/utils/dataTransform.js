/**
 * 数据转换工具 - 将数据库API数据转换为思维导图格式
 * 按照用户要求重新设计：6个顶级节点（5个表+excel链接）
 */

/**
 * 将API返回的数据转换为思维导图需要的树形结构
 * @param {Object} allData - API返回的包含所有表数据的对象
 * @param {Object} userInfo - 用户基本信息（从搜索API获取）
 * @returns {Object} 思维导图格式的数据
 */
export function transformToMindMapData(allData, userInfo = null) {
  if (!allData || typeof allData !== 'object') {
    return {
      data: { text: "暂无数据" },
      children: []
    };
  }

  const {
    users = [],
    transactions = [],
    asset_movements = [],
    login_logs = [],
    devices = [],
    source_files = []
  } = allData;

  // 构建根节点标题
  const userId = userInfo?.user_id || 
    users[0]?.user_id || 
    transactions[0]?.user_id || 
    "未知用户";
  
  const userName = userInfo?.name || users[0]?.name || "";
  const rootTitle = userName ? 
    `${userName} (${userId}) 调证数据` : 
    `用户 ${userId} 调证数据`;

  return {
    data: { 
      text: rootTitle,
      expand: true // 根节点默认展开
    },
    children: [
      buildUsersSection(users),
      buildTransactionsSection(transactions),
      buildAssetMovementsSection(asset_movements),
      buildLoginLogsSection(login_logs),
      buildDevicesSection(devices),
      buildSourceFilesSection(source_files)
    ]
  };
}

/**
 * 构建用户信息部分（users表）- 直接展示字段
 */
function buildUsersSection(users) {
  const children = [];
  
  if (users && users.length > 0) {
    const user = users[0]; // 通常只有一个用户记录
    
    // 按需展示字段，有值才显示
    if (user.name) children.push({ data: { text: `姓名: ${user.name}` } });
    if (user.phone_number) children.push({ data: { text: `电话: ${user.phone_number}` } });
    if (user.email) children.push({ data: { text: `邮箱: ${user.email}` } });
    if (user.registration_time) {
      const regTime = new Date(user.registration_time).toLocaleString('zh-CN');
      children.push({ data: { text: `注册时间: ${regTime}` } });
    }
    if (user.source) children.push({ data: { text: `数据来源: ${user.source}` } });
  }
  
  if (children.length === 0) {
    children.push({ data: { text: "暂无用户信息" } });
  }

  return {
    data: { 
      text: `用户信息 (${users.length}条记录)`,
      expand: true // 第一层节点默认展开
    },
    children
  };
}

/**
 * 构建交易统计部分（transactions表）- 描述性统计
 */
function buildTransactionsSection(transactions) {
  const children = [];
  
  if (transactions && transactions.length > 0) {
    const stats = calculateTransactionStats(transactions);
    
    // 基本统计
    children.push({ data: { text: `总交易笔数: ${stats.totalCount}` } });
    
    if (stats.uniqueAssets > 0) {
      children.push({ data: { text: `涉及币种数: ${stats.uniqueAssets}` } });
    }
    
    if (stats.totalAmount > 0) {
      children.push({ data: { text: `总交易金额: ${stats.totalAmount.toLocaleString()}` } });
    }
    
    if (stats.timeRange.start && stats.timeRange.end) {
      children.push({ 
        data: { text: `时间范围: ${stats.timeRange.start} 至 ${stats.timeRange.end}` }
      });
    }
    
    // 交易类型统计
    if (Object.keys(stats.typeDistribution).length > 0) {
      const typeChildren = Object.entries(stats.typeDistribution).map(([type, count]) => ({
        data: { text: `${type}: ${count}笔` }
      }));
      children.push({
        data: { 
          text: "交易类型分布",
          expand: false // 第二层默认折叠
        },
        children: typeChildren
      });
    }
    
    // 币种统计
    if (Object.keys(stats.assetDistribution).length > 0) {
      const assetChildren = Object.entries(stats.assetDistribution)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 10) // 只显示前10个币种
        .map(([asset, count]) => ({
          data: { text: `${asset}: ${count}笔` }
        }));
      children.push({
        data: { 
          text: "主要币种分布",
          expand: false // 第二层默认折叠
        },
        children: assetChildren
      });
    }
  } else {
    children.push({ data: { text: "暂无交易记录" } });
  }

  return {
    data: { 
      text: `交易统计 (${transactions.length}条记录)`,
      expand: true // 第一层节点默认展开
    },
    children
  };
}

/**
 * 构建资产流水统计部分（asset_movements表）- 描述性统计
 */
function buildAssetMovementsSection(assetMovements) {
  const children = [];
  
  if (assetMovements && assetMovements.length > 0) {
    const stats = calculateAssetMovementStats(assetMovements);
    
    children.push({ data: { text: `总流水笔数: ${stats.totalCount}` } });
    
    if (stats.uniqueAssets > 0) {
      children.push({ data: { text: `涉及资产种类: ${stats.uniqueAssets}` } });
    }
    
    if (stats.totalQuantity > 0) {
      children.push({ data: { text: `总流水数量: ${stats.totalQuantity.toLocaleString()}` } });
    }
    
    if (stats.timeRange.start && stats.timeRange.end) {
      children.push({ 
        data: { text: `时间范围: ${stats.timeRange.start} 至 ${stats.timeRange.end}` }
      });
    }
    
    // 方向统计
    if (Object.keys(stats.directionDistribution).length > 0) {
      const dirChildren = Object.entries(stats.directionDistribution).map(([dir, count]) => ({
        data: { text: `${dir}: ${count}笔` }
      }));
      children.push({
        data: { 
          text: "流水方向分布",
          expand: false // 第二层默认折叠
        },
        children: dirChildren
      });
    }
    
    // 网络统计
    if (Object.keys(stats.networkDistribution).length > 0) {
      const netChildren = Object.entries(stats.networkDistribution)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5)
        .map(([network, count]) => ({
          data: { text: `${network}: ${count}笔` }
        }));
      children.push({
        data: { 
          text: "主要网络分布",
          expand: false // 第二层默认折叠
        },
        children: netChildren
      });
    }
  } else {
    children.push({ data: { text: "暂无资产流水记录" } });
  }

  return {
    data: { 
      text: `资产流水统计 (${assetMovements.length}条记录)`,
      expand: true // 第一层节点默认展开
    },
    children
  };
}

/**
 * 构建登录日志统计部分（login_logs表）- 按IP统计（限制数据量）
 */
function buildLoginLogsSection(loginLogs) {
  const children = [];
  
  if (loginLogs && loginLogs.length > 0) {
    // 按IP分组统计
    const ipStats = {};
    
    loginLogs.forEach(log => {
      const ip = log.login_ip || 'Unknown IP';
      if (!ipStats[ip]) {
        ipStats[ip] = {
          count: 0,
          records: []
        };
      }
      ipStats[ip].count++;
      ipStats[ip].records.push(log);
    });
    
    // 按次数排序，只取前10个IP
    const sortedIPs = Object.entries(ipStats)
      .sort(([,a], [,b]) => b.count - a.count)
      .slice(0, 10); // 限制只显示前10个IP
    
    sortedIPs.forEach(([ip, data]) => {
      // 每个IP最多显示5条登录记录
      const limitedRecords = data.records.slice(0, 5);
      const ipChildren = limitedRecords.map(log => {
        const time = log.login_time ? new Date(log.login_time).toLocaleString('zh-CN') : '未知时间';
        const device = log.device_id || '未知设备';
        return {
          data: { text: `${time} | 设备: ${device}` }
        };
      });
      
      // 如果有更多记录，添加提示
      if (data.count > 5) {
        ipChildren.push({
          data: { text: `... 还有 ${data.count - 5} 条记录` }
        });
      }
      
      children.push({
        data: { 
          text: `${ip} (${data.count}次)`,
          expand: false // IP节点默认折叠
        },
        children: ipChildren
      });
    });
    
    // 如果还有更多IP，添加汇总信息
    if (Object.keys(ipStats).length > 10) {
      children.push({
        data: { text: `... 还有 ${Object.keys(ipStats).length - 10} 个其他IP地址` }
      });
    }
  } else {
    children.push({ data: { text: "暂无登录记录" } });
  }

  return {
    data: { 
      text: `登录日志统计 (${loginLogs.length}条记录)`,
      expand: true // 第一层节点默认展开
    },
    children
  };
}

/**
 * 构建设备信息部分（devices表）- 直接列出数据（限制数量）
 */
function buildDevicesSection(devices) {
  const children = [];
  
  if (devices && devices.length > 0) {
    // 限制最多显示20个设备
    const limitedDevices = devices.slice(0, 20);
    
    limitedDevices.forEach((device, index) => {
      const deviceChildren = [];
      
      // 基本字段
      if (device.device_id) deviceChildren.push({ data: { text: `设备ID: ${device.device_id}` } });
      if (device.client_type) deviceChildren.push({ data: { text: `客户端类型: ${device.client_type}` } });
      if (device.ip_address) deviceChildren.push({ data: { text: `IP地址: ${device.ip_address}` } });
      if (device.add_time) {
        const addTime = new Date(device.add_time).toLocaleString('zh-CN');
        deviceChildren.push({ data: { text: `添加时间: ${addTime}` } });
      }
      if (device.source) deviceChildren.push({ data: { text: `数据来源: ${device.source}` } });
      
      // extra_data字段（简化显示）
      if (device.extra_data) {
        try {
          const extraData = typeof device.extra_data === 'string' 
            ? JSON.parse(device.extra_data) 
            : device.extra_data;
          
          // 只显示前5个字段
          const entries = Object.entries(extraData).slice(0, 5);
          entries.forEach(([key, value]) => {
            if (value !== null && value !== undefined && value !== '') {
              deviceChildren.push({ data: { text: `${key}: ${value}` } });
            }
          });
          
          // 如果还有更多字段
          if (Object.keys(extraData).length > 5) {
            deviceChildren.push({ data: { text: `... 还有 ${Object.keys(extraData).length - 5} 个字段` } });
          }
        } catch (e) {
          deviceChildren.push({ data: { text: `额外数据: ${device.extra_data}` } });
        }
      }
      
      const deviceTitle = device.device_id || device.client_type || `设备${index + 1}`;
      children.push({
        data: { 
          text: deviceTitle,
          expand: false // 设备节点默认折叠
        },
        children: deviceChildren
      });
    });
    
    // 如果还有更多设备
    if (devices.length > 20) {
      children.push({
        data: { text: `... 还有 ${devices.length - 20} 台设备` }
      });
    }
  } else {
    children.push({ data: { text: "暂无设备信息" } });
  }

  return {
    data: { 
      text: `设备信息 (${devices.length}台设备)`,
      expand: true // 第一层节点默认展开
    },
    children
  };
}

/**
 * 构建源文件链接部分
 */
function buildSourceFilesSection(sourceFiles) {
  const children = [];
  
  if (sourceFiles && sourceFiles.length > 0) {
    sourceFiles.forEach((fileInfo, index) => {
      // 检查是否是文件信息对象还是简单的文件名字符串
      if (typeof fileInfo === 'object' && fileInfo !== null) {
        // 完整的文件信息对象
        const fileChildren = [];
        
        if (fileInfo.original_filename) {
          fileChildren.push({ data: { text: `原文件名: ${fileInfo.original_filename}` } });
        }
        
        if (fileInfo.file_size) {
          fileChildren.push({ data: { text: `文件大小: ${fileInfo.file_size}` } });
        }
        
        if (fileInfo.upload_time) {
          fileChildren.push({ data: { text: `上传时间: ${fileInfo.upload_time}` } });
        }
        
        if (fileInfo.platform) {
          fileChildren.push({ data: { text: `平台: ${fileInfo.platform}` } });
        }
        
        if (fileInfo.record_count !== undefined && fileInfo.record_count !== null) {
          fileChildren.push({ data: { text: `记录数量: ${fileInfo.record_count}条` } });
        }
        
        if (fileInfo.status) {
          fileChildren.push({ data: { text: `处理状态: ${fileInfo.status}` } });
        }
        
        const fileName = fileInfo.original_filename || fileInfo.file_name || `文件${index + 1}`;
        children.push({
          data: { 
            text: fileName,
            expand: false // 文件节点默认折叠
          },
          children: fileChildren
        });
      } else {
        // 简单的文件名字符串（向后兼容）
        children.push({
          data: { text: fileInfo || `文件${index + 1}` }
        });
      }
    });
  } else {
    children.push({ data: { text: "暂无源文件信息" } });
  }

  return {
    data: { 
      text: `Excel源文件 (${sourceFiles.length}个文件)`,
      expand: true // 第一层节点默认展开
    },
    children
  };
}

/**
 * 计算交易统计信息
 */
function calculateTransactionStats(transactions) {
  const stats = {
    totalCount: transactions.length,
    totalAmount: 0,
    uniqueAssets: 0,
    timeRange: { start: null, end: null },
    typeDistribution: {},
    assetDistribution: {}
  };
  
  const assets = new Set();
  const times = [];
  
  transactions.forEach(tx => {
    // 金额统计
    if (tx.total_amount && !isNaN(tx.total_amount)) {
      stats.totalAmount += parseFloat(tx.total_amount);
    }
    
    // 资产统计
    if (tx.base_asset) {
      assets.add(tx.base_asset);
      stats.assetDistribution[tx.base_asset] = (stats.assetDistribution[tx.base_asset] || 0) + 1;
    }
    
    // 交易类型统计
    if (tx.transaction_type) {
      stats.typeDistribution[tx.transaction_type] = (stats.typeDistribution[tx.transaction_type] || 0) + 1;
    }
    
    // 时间统计
    if (tx.transaction_time) {
      times.push(new Date(tx.transaction_time));
    }
  });
  
  stats.uniqueAssets = assets.size;
  
  if (times.length > 0) {
    times.sort();
    stats.timeRange.start = times[0].toLocaleDateString('zh-CN');
    stats.timeRange.end = times[times.length - 1].toLocaleDateString('zh-CN');
  }
  
  return stats;
}

/**
 * 计算资产流水统计信息
 */
function calculateAssetMovementStats(movements) {
  const stats = {
    totalCount: movements.length,
    totalQuantity: 0,
    uniqueAssets: 0,
    timeRange: { start: null, end: null },
    directionDistribution: {},
    networkDistribution: {}
  };
  
  const assets = new Set();
  const times = [];
  
  movements.forEach(mv => {
    // 数量统计
    if (mv.quantity && !isNaN(mv.quantity)) {
      stats.totalQuantity += parseFloat(mv.quantity);
    }
    
    // 资产统计
    if (mv.asset) {
      assets.add(mv.asset);
    }
    
    // 方向统计
    if (mv.direction) {
      stats.directionDistribution[mv.direction] = (stats.directionDistribution[mv.direction] || 0) + 1;
    }
    
    // 网络统计
    if (mv.network) {
      stats.networkDistribution[mv.network] = (stats.networkDistribution[mv.network] || 0) + 1;
    }
    
    // 时间统计
    if (mv.transaction_time) {
      times.push(new Date(mv.transaction_time));
    }
  });
  
  stats.uniqueAssets = assets.size;
  
  if (times.length > 0) {
    times.sort();
    stats.timeRange.start = times[0].toLocaleDateString('zh-CN');
    stats.timeRange.end = times[times.length - 1].toLocaleDateString('zh-CN');
  }
  
  return stats;
}

/**
 * 构建资产分析部分
 */
function buildAssetSection(assetStats) {
  return {
    data: { text: "资产分析" },
    children: Object.entries(assetStats).map(([asset, data]) => ({
      data: { text: asset },
      children: [
        { data: { text: `交易次数: ${data.count}次` } },
        { data: { text: `总数量: ${data.totalQuantity.toFixed(6)}` } },
        { data: { text: `总金额: ${data.totalAmount.toFixed(2)} USDT` } },
        { data: { text: `平均价格: ${data.avgPrice.toFixed(4)} USDT` } },
        { data: { text: `价格区间: ${data.minPrice.toFixed(4)} - ${data.maxPrice.toFixed(4)} USDT` } }
      ]
    }))
  };
}

/**
 * 构建交易记录部分
 */
function buildTransactionSection(transactionsByDate) {
  return {
    data: { text: "交易记录" },
    children: Object.entries(transactionsByDate)
      .sort(([a], [b]) => new Date(b) - new Date(a)) // 按日期降序
      .slice(0, 10) // 只显示最近10天
      .map(([date, transactions]) => ({
        data: { text: `${date} (${transactions.length}笔)` },
        children: transactions.map(tx => ({
          data: { 
            text: `${tx.transaction_time.split(' ')[1]} | ${tx.base_asset}/${tx.quote_asset} | 价格:${tx.price} | 数量:${tx.quantity} | 金额:${tx.total_amount.toFixed(2)}`
          }
        }))
      }))
  };
}

/**
 * 构建时间分析部分
 */
function buildTimeAnalysisSection(transactionData) {
  const timeStats = analyzeTimePatterns(transactionData);
  
  return {
    data: { text: "时间模式分析" },
    children: [
      {
        data: { text: "活跃时段" },
        children: Object.entries(timeStats.hourDistribution)
          .sort(([,a], [,b]) => b - a)
          .slice(0, 5)
          .map(([hour, count]) => ({
            data: { text: `${hour}:00-${hour}:59 (${count}笔)` }
          }))
      },
      {
        data: { text: "交易频率" },
        children: [
          { data: { text: `最活跃日期: ${timeStats.mostActiveDate.date} (${timeStats.mostActiveDate.count}笔)` } },
          { data: { text: `平均日交易量: ${timeStats.avgDailyTransactions.toFixed(1)}笔` } }
        ]
      }
    ]
  };
}

/**
 * 计算基本统计信息
 */
function calculateStats(transactions) {
  const totalTransactions = transactions.length;
  const totalAmount = transactions.reduce((sum, tx) => sum + (tx.total_amount || 0), 0);
  
  const dates = transactions
    .map(tx => tx.transaction_time.split(' ')[0])
    .filter(Boolean)
    .sort();
  
  const uniqueAssets = new Set(transactions.map(tx => tx.base_asset)).size;
  
  const transactionTypes = transactions.reduce((acc, tx) => {
    const type = tx.transaction_type || 'UNKNOWN';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {});

  return {
    totalTransactions,
    totalAmount,
    uniqueAssets,
    transactionTypes,
    dateRange: {
      start: dates[0] || 'N/A',
      end: dates[dates.length - 1] || 'N/A'
    }
  };
}

/**
 * 按日期分组交易
 */
function groupTransactionsByDate(transactions) {
  return transactions.reduce((acc, tx) => {
    const date = tx.transaction_time.split(' ')[0];
    if (!acc[date]) acc[date] = [];
    acc[date].push(tx);
    return acc;
  }, {});
}

/**
 * 计算资产统计
 */
function calculateAssetStats(transactions) {
  return transactions.reduce((acc, tx) => {
    const asset = tx.base_asset;
    if (!acc[asset]) {
      acc[asset] = {
        count: 0,
        totalQuantity: 0,
        totalAmount: 0,
        prices: []
      };
    }
    
    acc[asset].count++;
    acc[asset].totalQuantity += tx.quantity || 0;
    acc[asset].totalAmount += tx.total_amount || 0;
    if (tx.price > 0) acc[asset].prices.push(tx.price);
    
    return acc;
  }, {});
}

/**
 * 分析时间模式
 */
function analyzeTimePatterns(transactions) {
  const hourDistribution = {};
  const dateDistribution = {};
  
  transactions.forEach(tx => {
    // 提取小时
    const hour = new Date(tx.transaction_time).getHours();
    hourDistribution[hour] = (hourDistribution[hour] || 0) + 1;
    
    // 提取日期
    const date = tx.transaction_time.split(' ')[0];
    dateDistribution[date] = (dateDistribution[date] || 0) + 1;
  });
  
  const mostActiveDate = Object.entries(dateDistribution)
    .sort(([,a], [,b]) => b - a)[0];
  
  const avgDailyTransactions = Object.values(dateDistribution)
    .reduce((sum, count) => sum + count, 0) / Object.keys(dateDistribution).length;

  return {
    hourDistribution,
    mostActiveDate: {
      date: mostActiveDate?.[0] || 'N/A',
      count: mostActiveDate?.[1] || 0
    },
    avgDailyTransactions
  };
}


