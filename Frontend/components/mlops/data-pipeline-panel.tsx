"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { toast } from "sonner"
import { 
  Database, 
  Plus, 
  MoreHorizontal,
  FileText,
  GitBranch,
  CheckCircle,
  AlertCircle,
  Clock,
  RefreshCw,
  BarChart3,
  AlertTriangle
} from "lucide-react"
import { useDataPipeline } from "@/lib/stores/mlops-store"
import { 
  type DataVersion, 
  type DataQualityReport,
  type DataTransformation,
  formatTimestamp, 
  getStatusColor, 
  getStatusText,
  mlopsApi 
} from "@/lib/mlops-api"
import { QualityReportSkeleton } from "@/components/ui/loading-skeleton"

export function DataPipelinePanel() {
  const { dataVersions, loading, error, fetch, getQualityReport, qualityReports } = useDataPipeline()
  const [transformations, setTransformations] = useState<DataTransformation[]>([])
  const [selectedVersion, setSelectedVersion] = useState<DataVersion | null>(null)
  const [qualityReport, setQualityReport] = useState<DataQualityReport | null>(null)
  const [qualityReportLoading, setQualityReportLoading] = useState(false)
  const [createTransformDialogOpen, setCreateTransformDialogOpen] = useState(false)
  const [qualityDialogOpen, setQualityDialogOpen] = useState(false)
  const [activeTab, setActiveTab] = useState("versions")

  // Form state for creating transformation
  const [newTransformation, setNewTransformation] = useState({
    source_version_id: "",
    target_dataset_name: "",
    transformations: [{ type: "normalize", parameters: {} }]
  })

  useEffect(() => {
    fetchDataVersions()
    fetchTransformations()
  }, [])

  const fetchDataVersions = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await mlopsApi.getDataVersions({
        page: 1,
        per_page: 50
      })
      
      if (response.status === 'success' && response.data) {
        setDataVersions(response.data.versions)
      } else {
        setError(response.error || 'Failed to fetch data versions')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const fetchTransformations = async () => {
    try {
      // Note: This would be a separate endpoint in a real implementation
      // For now, we'll simulate some transformation data
      setTransformations([])
    } catch (err) {
      console.error('Failed to fetch transformations:', err)
    }
  }

  const handleViewQualityReport = async (version: DataVersion) => {
    try {
      setSelectedVersion(version)
      setQualityReport(null)
      setQualityDialogOpen(true)
      
      const response = await mlopsApi.getDataQualityReport(version.id)
      
      if (response.status === 'success' && response.data) {
        setQualityReport(response.data)
      } else {
        setError(response.error || 'Failed to fetch quality report')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  const handleCreateTransformation = async () => {
    try {
      if (!newTransformation.source_version_id) {
        alert('Source version is required')
        return
      }

      const response = await mlopsApi.createDataTransformation({
        source_version_id: newTransformation.source_version_id,
        transformations: newTransformation.transformations,
        target_dataset_name: newTransformation.target_dataset_name || undefined
      })

      if (response.status === 'success') {
        setCreateTransformDialogOpen(false)
        setNewTransformation({
          source_version_id: "",
          target_dataset_name: "",
          transformations: [{ type: "normalize", parameters: {} }]
        })
        fetchTransformations()
      } else {
        alert(response.error || 'Failed to create transformation')
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  const getQualityStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'excellent':
      case 'good':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'fair':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />
      case 'poor':
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      default:
        return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading data pipeline...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-16 bg-muted rounded"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-center">
            <AlertTriangle className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Data Pipeline Management</h3>
        <Dialog open={createTransformDialogOpen} onOpenChange={setCreateTransformDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Create Transformation
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Data Transformation</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="source-version">Source Data Version</Label>
                <Select 
                  value={newTransformation.source_version_id} 
                  onValueChange={(value) => setNewTransformation(prev => ({ ...prev, source_version_id: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select source version" />
                  </SelectTrigger>
                  <SelectContent>
                    {dataVersions.map((version) => (
                      <SelectItem key={version.id} value={version.id}>
                        {version.dataset_name} v{version.version}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="target-dataset">Target Dataset Name (optional)</Label>
                <Input
                  id="target-dataset"
                  value={newTransformation.target_dataset_name}
                  onChange={(e) => setNewTransformation(prev => ({ ...prev, target_dataset_name: e.target.value }))}
                  placeholder="e.g., cleaned_dataset"
                />
              </div>
              <div>
                <Label>Transformation Type</Label>
                <Select 
                  value={newTransformation.transformations[0]?.type || "normalize"} 
                  onValueChange={(value) => setNewTransformation(prev => ({ 
                    ...prev, 
                    transformations: [{ type: value, parameters: {} }] 
                  }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="normalize">Normalize</SelectItem>
                    <SelectItem value="remove_outliers">Remove Outliers</SelectItem>
                    <SelectItem value="fill_missing">Fill Missing Values</SelectItem>
                    <SelectItem value="encode_categorical">Encode Categorical</SelectItem>
                    <SelectItem value="feature_scaling">Feature Scaling</SelectItem>
                    <SelectItem value="custom">Custom Transformation</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setCreateTransformDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateTransformation}>
                  Create Transformation
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Data Pipeline Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="versions" className="flex items-center gap-2">
            <Database className="w-4 h-4" />
            Data Versions
          </TabsTrigger>
          <TabsTrigger value="transformations" className="flex items-center gap-2">
            <GitBranch className="w-4 h-4" />
            Transformations
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="versions">
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Dataset</TableHead>
                    <TableHead>Version</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Quality</TableHead>
                    <TableHead>Size</TableHead>
                    <TableHead>Records</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="w-12"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {dataVersions.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8">
                        <div className="flex flex-col items-center gap-2">
                          <Database className="h-8 w-8 text-muted-foreground" />
                          <p className="text-sm text-muted-foreground">No data versions found</p>
                          <p className="text-xs text-muted-foreground">
                            Data versions will appear here once your pipeline is active
                          </p>
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    dataVersions.map((version) => (
                      <TableRow key={version.id}>
                        <TableCell>
                          <div className="font-medium">{version.dataset_name}</div>
                        </TableCell>
                        <TableCell>
                          <span className="font-mono text-sm">{version.version}</span>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant="outline" 
                            className={`${getStatusColor(version.status)}/10 border-${getStatusColor(version.status).replace('bg-', '')}/20`}
                          >
                            {getStatusText(version.status)}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getQualityStatusIcon(version.quality_status)}
                            <span className="text-sm">{(version.quality_score * 100).toFixed(1)}%</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-sm">
                          {formatBytes(version.size_bytes)}
                        </TableCell>
                        <TableCell className="text-sm">
                          {version.record_count.toLocaleString()}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {formatTimestamp(version.created_at)}
                        </TableCell>
                        <TableCell>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleViewQualityReport(version)}
                          >
                            <BarChart3 className="w-4 h-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="transformations">
          <Card>
            <CardContent className="p-6">
              <div className="text-center py-8">
                <GitBranch className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">Data transformations will appear here</p>
                <p className="text-xs text-muted-foreground">
                  Create a transformation to start building your data pipeline
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Quality Report Dialog */}
      <Dialog open={qualityDialogOpen} onOpenChange={setQualityDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              Data Quality Report - {selectedVersion?.dataset_name} v{selectedVersion?.version}
            </DialogTitle>
          </DialogHeader>
          {qualityReport ? (
            <div className="space-y-6">
              {/* Overall Score */}
              <div className="text-center">
                <div className="text-3xl font-bold mb-2">
                  {(qualityReport.overall_score * 100).toFixed(1)}%
                </div>
                <Badge 
                  variant="outline" 
                  className={`${getStatusColor(qualityReport.overall_status)}/10 border-${getStatusColor(qualityReport.overall_status).replace('bg-', '')}/20`}
                >
                  {getStatusText(qualityReport.overall_status)}
                </Badge>
              </div>

              {/* Quality Dimensions */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Completeness</span>
                    <span>{(qualityReport.completeness_score * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={qualityReport.completeness_score * 100} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Consistency</span>
                    <span>{(qualityReport.consistency_score * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={qualityReport.consistency_score * 100} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Accuracy</span>
                    <span>{(qualityReport.accuracy_score * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={qualityReport.accuracy_score * 100} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Timeliness</span>
                    <span>{(qualityReport.timeliness_score * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={qualityReport.timeliness_score * 100} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Validity</span>
                    <span>{(qualityReport.validity_score * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={qualityReport.validity_score * 100} className="h-2" />
                </div>
              </div>

              {/* Issues and Recommendations */}
              {qualityReport.issues_found.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">Issues Found</h4>
                  <ul className="text-sm space-y-1">
                    {qualityReport.issues_found.map((issue, index) => (
                      <li key={index} className="flex items-center gap-2">
                        <AlertCircle className="w-3 h-3 text-yellow-500" />
                        {issue}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {qualityReport.recommendations.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">Recommendations</h4>
                  <ul className="text-sm space-y-1">
                    {qualityReport.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-center gap-2">
                        <CheckCircle className="w-3 h-3 text-green-500" />
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="w-6 h-6 animate-spin mr-2" />
              Loading quality report...
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
