local function lx(blocks) return pandoc.write(pandoc.Pandoc(blocks), 'latex') end
local function cell_tex(c)
  local t = lx(c.contents):gsub('\n\n', ' \\newline '):gsub('\n', ' ')
  return t
end
local function plain(len_acc, c) return len_acc + #pandoc.utils.stringify(c.contents) end

function Link(el)
  if el.target:match('^https?://') then return el end
  return el.content   -- relative repo links: keep text only
end

function Table(tbl)
  local head = tbl.head.rows
  local rows = {}
  for _, b in ipairs(tbl.bodies) do for _, r in ipairs(b.body) do table.insert(rows, r) end end
  local ncol = #tbl.colspecs
  -- measure text length per column
  local w = {}
  for i = 1, ncol do w[i] = 4 end
  local all = {}
  for _, r in ipairs(head) do table.insert(all, r) end
  for _, r in ipairs(rows) do table.insert(all, r) end
  local total = 0
  for _, r in ipairs(all) do
    for i, c in ipairs(r.cells) do
      local n = #pandoc.utils.stringify(c.contents)
      if n > w[i] then w[i] = n end
    end
  end
  for i = 1, ncol do total = total + w[i] end
  local wide = total > 75
  local env = wide and 'table*' or 'table'
  local width = wide and '\\textwidth' or '\\columnwidth'
  local spec = {}
  for i = 1, ncol do
    if w[i] > 14 then
      local frac = math.max(0.4, w[i] / total * ncol)
      table.insert(spec, string.format('>{\\raggedright\\arraybackslash\\hsize=%.2f\\hsize}X', frac))
    else table.insert(spec, 'l') end
  end
  -- normalise X hsizes so they sum to number of X cols
  local xs, sum = 0, 0
  for _, s in ipairs(spec) do local f = s:match('hsize=([%d%.]+)') if f then xs = xs + 1; sum = sum + tonumber(f) end end
  for i, s in ipairs(spec) do
    local f = s:match('hsize=([%d%.]+)')
    if f then spec[i] = s:gsub('hsize=[%d%.]+', string.format('hsize=%.3f', tonumber(f) * xs / sum)) end
  end
  local out = {}
  table.insert(out, '\\begin{' .. env .. '}[!t]\\centering\\footnotesize\\renewcommand{\\arraystretch}{1.15}\\setlength{\\tabcolsep}{4pt}')
  if xs > 0 then
    table.insert(out, '\\begin{tabularx}{' .. width .. '}{' .. table.concat(spec, '') .. '}\\toprule')
  else
    table.insert(out, '\\begin{adjustbox}{max width=' .. width .. '}\\begin{tabular}{' .. table.concat(spec, '') .. '}\\toprule')
  end
  for _, r in ipairs(head) do
    local cs = {} for _, c in ipairs(r.cells) do table.insert(cs, '\\textbf{' .. cell_tex(c) .. '}') end
    table.insert(out, table.concat(cs, ' & ') .. ' \\\\ \\midrule')
  end
  for _, r in ipairs(rows) do
    local cs = {} for _, c in ipairs(r.cells) do table.insert(cs, cell_tex(c)) end
    table.insert(out, table.concat(cs, ' & ') .. ' \\\\')
  end
  table.insert(out, '\\bottomrule')
  table.insert(out, xs > 0 and '\\end{tabularx}' or '\\end{tabular}\\end{adjustbox}')
  table.insert(out, '\\end{' .. env .. '}')
  return pandoc.RawBlock('latex', table.concat(out, '\n'))
end

function Figure(fig)
  local img
  pandoc.walk_block(fig, { Image = function(i) img = i end })
  if not img then return nil end
  local cap = pandoc.utils.stringify(img.caption)
  if cap == '' then cap = pandoc.utils.stringify(fig.caption) end
  local ratio = tonumber(img.attributes['ratio'] or '2')
  local wide = ratio > 2.9
  local env = wide and 'figure*' or 'figure'
  local width = wide and '0.85\\textwidth' or '\\columnwidth'
  return pandoc.RawBlock('latex', string.format(
    '\\begin{%s}[!t]\\centering\\includegraphics[width=%s]{%s}\\caption{%s}\\end{%s}',
    env, width, img.src, lx({pandoc.Plain(img.caption)}):gsub('\n',' '), env))
end
